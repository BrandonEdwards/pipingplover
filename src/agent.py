from .nest import Nest
from scipy.stats import truncnorm
import numpy as np
import src.utilities as util

class Agent(object):
	def __init__(self, ID, habitatType):
		self.agentID = ID
		self.habitatType = int(habitatType)
		self.humanPresence = False
		self.predatorPresence = False
		self.nestInfo = None
		self.chickWeight = list()
		self.closestNest = 0

	def getAgentID(self):
		"""Return agent ID (integer) of the given agent."""
		return self.agentID

	def getHabitatType(self):
		"""Return habitat type (integer) of the given agent."""
		return self.habitatType

	def isEmpty(self):
		"""Return a boolean value as to whether the agent is empty."""
		if len(self.chickWeight) == 0:
			return True
		else:
			return False

	def attemptNest(self, availableNests, time):
		"""Attempt a nest and return boolean value on success or failure.

		Keyword arguments:
		availableNests  --  The total number of potential nests still available based
							on number of adults in the simulation.
		time            --  Current time in the simulation. Future implementations may
							reduce nesting probability based on this time.

		Pull a number from random Bernoulli trial. If success, create a nest in the agent.
		Otherwise return.
		"""
		if self.nestInfo != None:
			return 0

		numNests = np.random.binomial(availableNests, 0.00001, 1)
		if numNests > 0:
			self.nestInfo = Nest(time)
			print("Nest successfully created in agent ", self.agentID, " at time ", time)
			return True
		else:
			return False

	def isNest(self):
		"""Check if agent contains a nest and return boolean value."""
		if self.nestInfo == None:
			return False
		else:
			return True

	def layEgg(self, time):
		"""Attempt to lay an egg based on time in simulation.

		Keyword arguments:
		time 			--	Current time in simulation. Used to match up with egg laying
							times of the nest.
		"""
		if self.nestInfo.layEgg(time) == 1:
			print("Laid egg at nest in agent ", self.agentID)

	def checkHatchTime(self, time):
		"""Check if eggs should hatch based on time in simulation.

		Keyword arguments:
		time 			--	Current time in simulation. Used to match up with egg hatching
							times of the nest.

		Call hatch() function from Nest() class. If it returns a list of hatch weights,
		then the nest has successfully hatched. Add this list of weights to the chick
		weight of the current agent.
		"""
		weights = self.nestInfo.hatch(time)
		if weights != None:
			for weight in weights:
				self.chickWeight.append(weight)
				
			print("Chicks successfully hatched in agent ", self.agentID, " with weights: ", self.chickWeight)

	def isHumanPresence(self):
		"""Check if humans are present in the agent, return boolean."""
		return self.humanPresence

	def flush(self):
		"""If humans are present in cell, move chicks away from humans."""
		pass

	def forage(self, energyVector):
		"""Increase weight of chicks in given agent based on habitat type.

		Keyword arguments:
		energyVector 	--	Energy multiplier indexed by habitat type

		Check if there are humans in alert distance of the agent. If so, increase
		chick weight vector by a reduced rate (half), otherwise increase chick weight
		vector by full amount. Get habitat type energy multiplier by indexing energyVector
		with habitat type.
		"""
		if len(self.chickWeight) > 0:
			if self.humanInAlertDistance() == False:
				#multiply all elements in chick energy by energy gain
				self.chickWeight = [i + (0.007 * energyVector[self.habitatType]) for i in self.chickWeight]
			else:
				self.chickWeight = [i + (0.0035 * energyVector[self.habitatType]) for i in self.chickWeight]

	def move(self, agentDB, IDToAgent, habitatVector, energyVector, mapWidth):
		"""Attempt to move chicks to different agent to forage.

		Keyword arguments:
		agentDB			--	List of all agents in the simulation
		IDToAgent		--	Dictionary mapping agent IDs to their index in agentDB
		habitatVector	--	1D list of all habitat types contained in environment (row major)
		energyVector 	--	Energy multiplier indexed by habitat type
		mapWidth		--	Width of the total simulation environment

		Create a map matrix 25 cells wide for all possible move choices. After getting
		rid of all move choices that are outside of the given environment, convert the
		agentIDs to their respective energy levels (as given by energyVector, higher energy
		level indicated better foraging zone). Normalize these values and pull from
		multinomial distribution to find index of what agent the chicks will move to.
		Copy the chick weights to the new agent and assign an empty chick weight list
		to the current agent.
		"""
		moveChoices = util.createMapMatrix(self.agentID, 25, mapWidth)

		#Get rid of all move choices that are out of environment (if necessary)
		moveChoices = [i for i in moveChoices if habitatVector[i] > -1]

		#Convert all to agent IDs to their respective habitat type
		moveChoicesHabitat = [habitatVector[i] for i in moveChoices]

		#Convert all habitat types to energyVectors
		moveChoicesEnergy = [energyVector[i] for i in moveChoicesHabitat]

		#Normalize the movement choice energy vectors
		probabilities = [float(i)/sum(moveChoices) for i in moveChoices]

		#Pull from multinomial distribution and get index of the success (i.e. new agent).
		moveLocationArray = np.random.multinomial(1, probabilities, size = 1)
		moveLocationIndex = -1
		for i in range(0, len(moveLocationArray[0])):
			if moveLocationArray[0][i] == 1:
				moveLocationIndex = i
				break

		if moveLocationIndex == -1:
			return agentDB

		newAgentID = moveChoices[moveLocationIndex]

		if newAgentID == self.agentID:
			print("No movement")
			return agentDB
		
		agentDB[IDToAgent[newAgentID]].chickWeight.extend(self.chickWeight)
		self.chickWeight = list()

		return agentDB

	def humanInAlertDistance(self):
		"""Check if there are humans within alert distance (50m), return boolean."""
		return False

	def chickAtNest(self):
		"""Check if there are chicks in an agent that is not a nest. Return boolean."""
		if self.nestInfo == None and len(self.chickWeight) > 0:
			return False
		else:
			return True

	def rest(self):
		"""Check for humans in a reduced alert distance"""
		pass

	def findNearestNest(self, agentDB, IDToAgent, habitatVector, mapWidth):
		"""Find location of nearest nest and move chicks to that agent.

		Keyword arguments:
		agentDB			--	List of all agents in the simulation
		IDToAgent		--	Dictionary mapping agent IDs to their index in agentDB
		habitatVector	--	1D list of all habitat types contained in environment (row major)
		mapWidth		--	Width of the total simulation environment

		Create a map matrix 200 cells wide. After ridding of non-environment cells,
		check for any cells containing a nest. If a nest exists, move chick vector
		to that agent.

		TO DO:
		If no nest exist, find agent that would bring the chicks closest to a nest
		to try again next time step. One way to implement this would be to store
		a "nearest nest" attribute in each given agent, calculated at the beginning
		of the simulation when nesting occurs, that assists in moving chicks in the
		direction of the nearest nest.
		"""
		moveChoices = util.createMapMatrix(self.agentID, 200, mapWidth)
		moveChoices = [i for i in moveChoices if habitatVector[i] > -1]
		newAgentID = -1
		for ID in moveChoices:
			if agentDB[IDToAgent[ID]].nestInfo != None:
				newAgentID = ID
				break

		if (newAgentID > -1):
			print("Found nest at ", agentDB[IDToAgent[newAgentID]].getAgentID())
			agentDB[IDToAgent[newAgentID]].chickWeight.extend(self.chickWeight)
			self.chickWeight = list()
		else:
			print("No nearby nest found")


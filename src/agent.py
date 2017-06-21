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
        return self.agentID

    def getHabitatType(self):
        return self.habitatType

    def isEmpty(self):
        if len(self.chickWeight) == 0:
            return True
        else:
            return False

    def attemptNest(self, availableNests, time):
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
        if self.nestInfo == None:
            return False
        else:
            return True

    def layEgg(self, time):
        if self.nestInfo.layEgg(time) == 1:
            print("Laid egg at nest in agent ", self.agentID)

    def checkHatchTime(self, time):
        weights = self.nestInfo.hatch(time)
        if weights != None:
            for weight in weights:
                self.chickWeight.append(weight)
                
            print("Chicks successfully hatched in agent ", self.agentID, " with weights: ", self.chickWeight)

    def isHumanPresence(self):
        return self.humanPresence

    def flush(self):
        pass

    def forage(self, energyVector):
        if len(self.chickWeight) > 0:
            if self.humanInAlertDistance() == False:
                #multiply all elements in chick energy by energy gain
                self.chickWeight = [i + (0.007 * energyVector[self.habitatType]) for i in self.chickWeight]
            else:
                self.chickWeight = [i + (0.0035 * energyVector[self.habitatType]) for i in self.chickWeight]

    def move(self, agentDB, IDToAgent, habitatVector, energyVector, mapWidth):
        moveChoices = util.createMapMatrix(self.agentID, 25, mapWidth)

        #Get rid of all move choices that are out of environment (if necessary)
        moveChoices = [i for i in moveChoices if habitatVector[i] > -1]

        #Convert all to agent IDs to their respective habitat type
        moveChoicesHabitat = [habitatVector[i] for i in moveChoices]

        #Convert all habitat types to energyVectors
        moveChoicesEnergy = [energyVector[i] for i in moveChoicesHabitat]

        #Normalize the movement choice energy vectors
        moveLocationArray = np.random.multinomial(1, [float(i)/sum(moveChoices) for i in moveChoices], size = 1)
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
            
        #print(self.agentID, " ----------------------> ", agentDB[IDToAgent[newAgentID]].getAgentID())
        #print(self.chickWeight, " ", agentDB[IDToAgent[newAgentID]].chickWeight)
        agentDB[IDToAgent[newAgentID]].chickWeight.extend(self.chickWeight)
        self.chickWeight = list()
        #print(self.chickWeight, " ", agentDB[IDToAgent[newAgentID]].chickWeight)

        return agentDB

    def humanInAlertDistance(self):
        return False

    def chickAtNest(self):
        if self.nestInfo == None and len(self.chickWeight) > 0:
            return False
        else:
            return True

    def rest(self):
        pass

    def findNearestNest(self):
        pass

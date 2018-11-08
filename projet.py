import sys
import random
from math import gcd

def LCM(numbers):
	"""
	Computing least common multiple
	"""
	lcm = numbers[0]
	for i in numbers[1:]:
	  lcm = lcm*i//gcd(lcm, i)
	return lcm

def readFile(filename):
	"""
	Reading system.txt file function which returns a list containing the values of offset, WCET and periods
	"""
	systemFile = open(filename, "r")
	systemList = systemFile.readlines()
	newSystemList = []
	for i in range(0,len(systemList)):
		newSystemList.append(systemList[i].replace(" ", "").strip("\n").split(";"))
	return newSystemList

def printFeasibilityInterval(newSystemList):
	"""
	Printing the feasibility interval of a list of offset, WCET and periods values
	from a system.txt file
	""" 
	offsetList = []
	wcetList = []
	periodList = []

	for i in range(0,len(newSystemList)):
		if(i==0):
			offsetList.append([row[i] for row in newSystemList])
		elif(i==1):
			wcetList.append([row[i] for row in newSystemList])
		else:
			periodList.append([row[i] for row in newSystemList])
	for i in range(0,len(periodList)):
		periodList[i] = [int(i) for i in periodList[i]]
		offsetList[i] = [int(i) for i in offsetList[i]]

	feasibilityIntervalUpperBound = max(offsetList[0]) + (2*LCM(periodList[0]))
	print("feasibility interval: 0 ," ,feasibilityIntervalUpperBound)


def matchRequiredUtilisationProcent(wcets, periods, procent, delta):
	"""
	Check wether or not we have our required utilisation procent with the values generated randomly
	"""
	result = 0
	for i in range (0, len(wcets)):
		result += wcets[i]/periods[i]
	if ((procent - delta) <= result <= (procent + delta)):
		print("Utilization =",result)
		return True
	return False


def generateTasks(numberOfTasks, requiredUtilisationProcent, delta):

	offsets = []
	for i in range(0, numberOfTasks):
		offsets.append(random.randint(0,2))

	loop = True
	while(loop):  #While we do not have our required utilisation procent
		wcets = []
		periods = []
		for i in range (0, numberOfTasks):
			wcets.append(random.randint(1,50))
			periods.append(random.randint(1,50))

		if matchRequiredUtilisationProcent(wcets, periods, requiredUtilisationProcent, delta):
			loop = False

	return offsets, wcets, periods


def systemFileGenerator(offsets, wcets, periods):
	
	file = open("tasks.txt", "w")
	for i in range(0, len(offsets)):
		file.write(str(offsets[i]) + "; " + str(wcets[i]) + "; " + str(periods[i]) + "\n")
	file.close
	


def main(filename):
	newSystemList = readFile(filename)
	
	# Testing feasibility interval print
	print("# QUESTION 1")
	printFeasibilityInterval(newSystemList)

	# Testing tasks generator 
	print("\n# QUESTION 2")
	numberOfTasks = 6
	requiredUtilisationProcent = 70
	delta = 2 #Margin of error accepted
	offsets, wcets, periods = generateTasks(numberOfTasks, requiredUtilisationProcent, delta)
	systemFileGenerator(offsets, wcets, periods)


main(sys.argv[1])
import sys
import random
import copy
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

def getOffsetWCETPeriodLists(systemList):
	offsetList = []
	wcetList = []
	periodList = []

	for i in range(len(systemList)):
		offsetList.append(int(systemList[i][0]))
		wcetList.append(int(systemList[i][1]))
		periodList.append(int(systemList[i][2]))

	return offsetList, wcetList, periodList 

def computeFeasibilityInterval(newSystemList):
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

	return feasibilityIntervalUpperBound

def printFeasibilityInterval(feasibilityIntervalUpperBound):
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

def getMultiplesOf(number, limit, offset):
	multiples = []
	count = 1
	multiple = count * int(number) + int(offset) 
	while(multiple <= limit):
		multiples.append(multiple)
		count += 1
		multiple = count * int(number) + int(offset) 

	return multiples 

def getTasksDeadlines(systemList, upperBound, offsets):

	tasksDeadlines = {}
	for i in range(len(systemList)):
		tasksDeadlines[i] = getMultiplesOf(systemList[i][2], upperBound, offsets[i])

	return tasksDeadlines

def getSmallestDeadlines(tasksDeadlinesDict):

	minVal = 9999
	i = 0
	index = 0 
	for listDeadlines in tasksDeadlinesDict.values():
		if (listDeadlines[0] < minVal):
			minVal = listDeadlines[0]
			index = i
		i += 1

	return index,minVal

def initJobsList(systemList):
	jobs = []
	for i in range(len(systemList)):
		jobs.append(0)
	return jobs


def isSchedulable(systemList, end):
	return end <= computeFeasibilityInterval(systemList)

# ATTENTION : gérer si même deadline 
def EDF(system, begin, end):
	systemList = readFile(system)
	jobs = initJobsList(systemList)

	offsetList = getOffsetWCETPeriodLists(systemList)[0]
	wcetList = getOffsetWCETPeriodLists(systemList)[1]
	periodList = getOffsetWCETPeriodLists(systemList)[2]

	tasksDeadlinesDict = getTasksDeadlines(systemList, end, offsetList)
	tasksExecuted = []

	if(isSchedulable):
		print("Schedule from", begin, "to", end, ";", len(systemList), "tasks")
		t = 0
		wcets = copy.deepcopy(wcetList)
		while(t <= end):
			taskNumber, smallest = getSmallestDeadlines(tasksDeadlinesDict)
			tasksExecuted.append(taskNumber)
			wcets[taskNumber] -= 1 

			for deadlineList in tasksDeadlinesDict.values():
				for deadline in deadlineList: 
					if(t == deadline):
						print(t, " : Arrival of job T{}J{}".format(list(tasksDeadlinesDict.keys())[list(tasksDeadlinesDict.values()).index(deadlineList)] , deadlineList.index(deadline) + 1 ))

			if(wcets[taskNumber] == 0):
				jobs[taskNumber] += 1
				wcets[taskNumber] = wcetList[taskNumber]
				tasksDeadlinesDict[taskNumber] = tasksDeadlinesDict[taskNumber][1:] 

			#print("{}-{} : T{}J{}".format(t,t+int(wcetList[taskNumber]),taskNumber,jobs[taskNumber]))

			t += 1
			print(tasksExecuted)


	
def main(filename):
	newSystemList = readFile(filename)
	print(newSystemList)
	offsets, wcets, periods = getOffsetWCETPeriodLists(newSystemList)
	print("ALO",wcets)

	print(getTasksDeadlines(newSystemList,20,[0,0,1]))
	
	print("\n")
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

	print("\n")
	EDF(filename, 0, 20)

if __name__ == "__main__":
	main(sys.argv[1])
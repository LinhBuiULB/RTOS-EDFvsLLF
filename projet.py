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

def getSmallestDeadlines(tasksDeadlinesDict, isJobDoneUntilNextDeadline):

	minVal = 9999
	i = 0
	current = 0 
	for listDeadlines in tasksDeadlinesDict.values():
		if len(listDeadlines) != 0:
			if (listDeadlines[0] < minVal and not isJobDoneUntilNextDeadline[i]):
				minVal = listDeadlines[0]
				current = i
		i += 1

	return current,minVal

def isDeadlineMissed(deadline, t):
	"""
	Check whether the deadline is missed or not
	"""
	return deadline <= t


def initJobsList(systemList):
	jobs = []
	for i in range(len(systemList)):
		jobs.append(0)
	return jobs

def initIsJobDoneDict(systemList):
	isJobDoneUntilNextDeadline = {}
	for i in range(len(systemList)):
		isJobDoneUntilNextDeadline[i] = False 
	return isJobDoneUntilNextDeadline

def isSchedulable(systemList, end):
	return end <= computeFeasibilityInterval(systemList)

def EDF(system, begin, end):
	systemList = readFile(system)
	jobs = initJobsList(systemList)

	offsetList, wcetList, periodList = getOffsetWCETPeriodLists(systemList)

	tasksDeadlinesDict = getTasksDeadlines(systemList, computeFeasibilityInterval(systemList), offsetList)
	tasksExecuted = []
	isJobDoneUntilNextDeadline = initIsJobDoneDict(systemList) # dict that allows us to get if the jobs are done for the currrent deadline 
	arrivalJob = copy.deepcopy(tasksDeadlinesDict)
	arrivalJobOutput = []

	if(isSchedulable):
		t = 0
		wcets = copy.deepcopy(wcetList)
		
		while(t <= end):

			for deadlineList in arrivalJob.values():
				for deadline in deadlineList: 
					if(t == deadline):
						isJobDoneUntilNextDeadline[list(arrivalJob.keys())[list(arrivalJob.values()).index(deadlineList)]] = False
						arrivalJobOutput.append("{}:T{}J{}".format(t, list(arrivalJob.keys())[list(arrivalJob.values()).index(deadlineList)] , deadlineList.index(deadline) + 1 ))

			currentExecutedTask, smallest = getSmallestDeadlines(tasksDeadlinesDict, isJobDoneUntilNextDeadline)
			if isDeadlineMissed(smallest, t):
				tasksExecuted.append("Missed")
				break

			tasksExecuted.append((currentExecutedTask, jobs[currentExecutedTask]))
			wcets[currentExecutedTask] -= 1 

			# if job done  
			if(wcets[currentExecutedTask] == 0):
				isJobDoneUntilNextDeadline[currentExecutedTask] = True
				jobs[currentExecutedTask] += 1
				wcets[currentExecutedTask] = wcetList[currentExecutedTask]
				tasksDeadlinesDict[currentExecutedTask] = tasksDeadlinesDict[currentExecutedTask][1:] 

			t += 1

		printOutputs(tasksExecuted, arrivalJobOutput, begin, end, systemList)

def printOutputs(tasksExecuted, arrivalJobOutput, begin, end, systemList):
	"""
	Print the schedule of the system when the schedule is over
	"""
	print("Schedule from", begin, "to", end, ";", len(systemList), "tasks")
	i=0
	while(i < len(tasksExecuted)-1):
		interval = getTaskInterval(tasksExecuted, tasksExecuted[i][0], i)
		if(i >= begin):
			print("{}-{} : T{}J{}".format(i, i+interval, tasksExecuted[i][0], tasksExecuted[i][1]))
		for j in range(i+1, i+interval+1):
			for elem in arrivalJobOutput:
				if int(elem.split(":")[0]) == j:
					print("{} : Arrival of job {}".format(j, elem.split(":")[1]))
		i+=interval
		if (tasksExecuted[i] == "Missed"):
			print("{}: Job T{}J{} misses a deadline".format(i, tasksExecuted[-2][0], tasksExecuted[-2][1]))
			print("END: 1 preemptions")
			break



def getTaskInterval(tasksExecuted, task, index):
	"""
	Give the interval during which the task has been executed in a row
	"""
	interval = 1
	index += 1
	while(tasksExecuted[index][0] == task):
		interval += 1
		index += 1
		if index == (len(tasksExecuted) - 1):
			break

	return interval

def main(filename):
	newSystemList = readFile(filename)
	print(newSystemList)
	offsets, wcets, periods = getOffsetWCETPeriodLists(newSystemList)
	print("ALO",wcets)

	print(getTasksDeadlines(newSystemList,25,[0,0,1]))
	
	# Testing feasibility interval print
	print("\n")
	print("# QUESTION 1")
	printFeasibilityInterval(newSystemList)

	# Testing tasks generator 
	print("\n# QUESTION 2")
	numberOfTasks = 6
	requiredUtilisationProcent = 70
	delta = 2 #Margin of error accepted
	offsets, wcets, periods = generateTasks(numberOfTasks, requiredUtilisationProcent, delta)
	systemFileGenerator(offsets, wcets, periods)

	# Testing tasks generator 
	print("\n# QUESTION 3")
	EDF(filename, 4, 25)

if __name__ == "__main__":
	main(sys.argv[1])
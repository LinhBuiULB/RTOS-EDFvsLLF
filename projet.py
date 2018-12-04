import sys
import random
import copy
from math import gcd
import matplotlib.pyplot as plt
import numpy as np
import string
import pylab as P

UPPER_BOUND_VALUE = 9999

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
	"""
	Get offset, WCET and period lists of all tasks 
	"""
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
    offsetList, wcetList, periodList = getOffsetWCETPeriodLists(newSystemList)
    feasibilityIntervalUpperBound = max(offsetList) + (2*LCM(periodList))

    return feasibilityIntervalUpperBound

def printFeasibilityInterval(feasibilityIntervalUpperBound):
	"""
	Print the feasibility interval (question 1)
	"""
	print("feasibility interval: 0 ," ,feasibilityIntervalUpperBound)

def matchRequiredUtilisationProcent(wcets, periods, procent, delta):
	"""
	Check whether or not we have our required utilisation procent with the values generated randomly
	"""
	result = 0
	for i in range (0, len(wcets)):
		result += wcets[i]/periods[i]
	if ((procent - delta) <= result <= (procent + delta)):
		print("Utilization =",result)
		return True
	return False

def generateTasks(numberOfTasks, requiredUtilisationProcent, delta):
	"""
	Generator of tasks 
	"""
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
	"""
	Generator tasks in a file (question 2)
	"""
	file = open("tasks.txt", "w")
	for i in range(0, len(offsets)):
		file.write(str(offsets[i]) + "; " + str(wcets[i]) + "; " + str(periods[i]) + "\n")
	file.close

def getMultiplesOf(number, limit, offset):
	"""
	Get all multiples of a number to get all deadlines of a task until the limit (feasibility interval)
	"""
	multiples = []
	count = 1
	multiple = count * int(number) + int(offset) 
	while(multiple <= limit):
		multiples.append(multiple)
		count += 1
		multiple = count * int(number) + int(offset) 

	return multiples 

def getTasksDeadlines(systemList, upperBound, offsets):
	"""
	Get all the deadlines for the tasks 
	"""
	tasksDeadlines = {}
	for i in range(len(systemList)):
		tasksDeadlines[i] = getMultiplesOf(systemList[i][2], upperBound, offsets[i])

	return tasksDeadlines

def getSmallestDeadlines(tasksDeadlinesDict, isJobDoneUntilNextDeadline):
	"""
	Get the smallest deadline and the corresponding task to know which one we have to execute currently 
	"""
	minVal = UPPER_BOUND_VALUE
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
	"""
	Initialize the list of jobs's tasks to 0 
	"""
	jobs = []
	for i in range(len(systemList)):
		jobs.append(0)
	return jobs

def initIsJobDoneDict(systemList):
	"""
	Initialize the dictionary that tells wheter or not the job is done until the next arrival of job
	"""
	isJobDoneUntilNextDeadline = {}
	for i in range(len(systemList)):
		isJobDoneUntilNextDeadline[i] = False 
	return isJobDoneUntilNextDeadline

def isSchedulable(systemList, end):
	"""
	Check if the system is schedulable
	"""
	return end <= computeFeasibilityInterval(systemList)

def computeLaxities(time, tasksDeadlines, e, isJobDoneUntilNextDeadline, CPUTimeUsed):
	"""
	Compute the laxity of all jobs
	"""
	newLaxities = [0 for i in range(len(isJobDoneUntilNextDeadline))]
	for i in range (len(isJobDoneUntilNextDeadline)):
		if isJobDoneUntilNextDeadline[i]:
			newLaxities[i] = UPPER_BOUND_VALUE
		else:
			newLaxities[i] = tasksDeadlines[i][0] - time - (e[i] - CPUTimeUsed[i])

	return newLaxities


def LLF(system, begin, end):
	"""
	LLF schedule
	"""
	systemList = readFile(system)
	jobs = initJobsList(systemList)
	offsetList, wcetList, periodList = getOffsetWCETPeriodLists(systemList)
	print("offsets",offsetList)
	tasksDeadlinesDict = getTasksDeadlines(systemList, computeFeasibilityInterval(systemList), offsetList)
	tasksExecuted = []
	isJobDoneUntilNextDeadline = initIsJobDoneDict(systemList) # dict that allows us to get if the jobs are done for the currrent deadline 
	arrivalJob = copy.deepcopy(tasksDeadlinesDict)
	arrivalJobOutput = []
	preemptionsNb = 0

	laxityOfJobs = []
	CPUTimeUsed = [0 for i in range(len(jobs))]

	if(isSchedulable):
		t = 0
		wcets = copy.deepcopy(wcetList)

		while(t <= end):

			for deadlineList in arrivalJob.values():
				for deadline in deadlineList: 
					if(t == deadline):
						isJobDoneUntilNextDeadline[list(arrivalJob.keys())[list(arrivalJob.values()).index(deadlineList)]] = False
						arrivalJobOutput.append("{}:T{}J{}".format(t, list(arrivalJob.keys())[list(arrivalJob.values()).index(deadlineList)] , deadlineList.index(deadline) + 1 ))


			laxityOfJobs = computeLaxities(t, tasksDeadlinesDict, wcetList, isJobDoneUntilNextDeadline, CPUTimeUsed)
			print("Laxities are {}".format(laxityOfJobs))

			currentExecutedTask = laxityOfJobs.index(min(laxityOfJobs))

			if (t != 0):
				if tasksExecuted[t-1][0] != currentExecutedTask:
					if not isJobDoneUntilNextDeadline[tasksExecuted[t-1][0]]:
						preemptionsNb += 1 

			CPUTimeUsed[currentExecutedTask] += 1
			wcets[currentExecutedTask] -= 1 
			tasksExecuted.append((currentExecutedTask, jobs[currentExecutedTask]))

			if(min(laxityOfJobs) < 0):
				print("Missed")
				tasksExecuted.append("Missed")
				break

			if(wcets[currentExecutedTask] == 0):
				isJobDoneUntilNextDeadline[currentExecutedTask] = True
				jobs[currentExecutedTask] += 1
				wcets[currentExecutedTask] = wcetList[currentExecutedTask]
				tasksDeadlinesDict[currentExecutedTask] = tasksDeadlinesDict[currentExecutedTask][1:] 
				CPUTimeUsed[currentExecutedTask] = 0

			print("Task executed are {} at time {} \n".format(tasksExecuted, t))

			t += 1

		printOutputs(tasksExecuted, arrivalJobOutput, begin, end, systemList, preemptionsNb)
		printGraph(tasksExecuted)


def EDF(system, begin, end):
	"""
	EDF schedule
	"""
	systemList = readFile(system)
	jobs = initJobsList(systemList)
	offsetList, wcetList, periodList = getOffsetWCETPeriodLists(systemList)
	tasksDeadlinesDict = getTasksDeadlines(systemList, computeFeasibilityInterval(systemList), offsetList)
	tasksExecuted = []
	isJobDoneUntilNextDeadline = initIsJobDoneDict(systemList) # dict that allows us to get if the jobs are done for the current deadline 
	arrivalJob = copy.deepcopy(tasksDeadlinesDict)
	arrivalJobOutput = []
	preemptionsNb = 0

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

			# Compute preemption number
			if (t != 0):
				if tasksExecuted[t-1][0] != currentExecutedTask:
					if not isJobDoneUntilNextDeadline[tasksExecuted[t-1][0]]:
						preemptionsNb += 1 

			# if job done  
			if(wcets[currentExecutedTask] == 0):
				isJobDoneUntilNextDeadline[currentExecutedTask] = True
				jobs[currentExecutedTask] += 1
				wcets[currentExecutedTask] = wcetList[currentExecutedTask]
				tasksDeadlinesDict[currentExecutedTask] = tasksDeadlinesDict[currentExecutedTask][1:]

			t += 1

		printOutputs(tasksExecuted, arrivalJobOutput, begin, end, systemList, preemptionsNb)
		printGraph(tasksExecuted, arrivalJob, offsetList)

def printOutputs(tasksExecuted, arrivalJobOutput, begin, end, systemList, preemptionsNb):
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
			print("END: {} preemptions".format(preemptionsNb))
			break

def printGraph(tasksExecuted, arrivalJob, offsetList):
	x = []
	y = []
	xCircle = []
	yCircle = [] 
	plt.figure(figsize=(15,13)) 
	
	"""
	create two arrays for the execution time to be plotted
	"""
	print("tasks;", tasksExecuted)
	for i in range(len(tasksExecuted)):
		if(tasksExecuted[i] != "Missed"):
			y.append(tasksExecuted[i][0])
			x.append(i)
		else:
			plt.text(i,tasksExecuted[i-1][0], "Job missed !",ha="center", va="center",bbox=dict(boxstyle="round",ec=(1., 0.5, 0.5),fc=(1., 0.8, 0.8),))


	"""
	create two arrays for the deadlines to be plotted and draw the arrows corresponding to the arrival
	"""
	for i in range(len(arrivalJob)):
		for deadline in arrivalJob[i]:
			yCircle.append(i)
			xCircle.append(deadline)
			jobArrival  = plt.arrow(deadline,i-0.35,0,0.2, fc="k", ec="k", head_width = 0.5, head_length = 0.1)

	"""
	draw the first arrival of the job of each tasks
	"""
	for i in range(len(offsetList)):
		firstJob =plt.arrow(offsetList[i]+0.05,i-0.35,0,0.2,fc="g", ec="g", head_width = 0.5, head_length = 0.1, linewidth = 2)

	y = np.array(y)
	x = np.array(x)		
	xCircle = np.array(xCircle)
	yCircle = np.array(yCircle)
	deadline = plt.scatter(xCircle, yCircle, s=120, linewidth = 2,facecolors='none', edgecolors='red', zorder=1)

	ylabels = []
	xlabels = [] 

	countX = 0 
	for j in range(len(x)+2):
		xlabels.append(countX)
		print(countX)
		countX += 1 
	
	xlabels = np.array(xlabels)
	
	countY = 0 
	for i in range(len(x)):
		ylabels.append(countY)
		countY += 1

	executionTime = plt.barh(y, [1]*len(x), left=x, color = 'blue', edgecolor = 'green', align='center', height=0.1, zorder = -1)
	plt.ylim(max(y)+0.5, min(y)-0.5)
	plt.xlim(min(x), max(x)+2)
	plt.yticks(np.arange(y.max()+1), ylabels)
	plt.xticks(np.arange(xlabels.max()+1), xlabels)
	plt.xlabel("t")
	plt.ylabel("Task number")
	plt.legend([jobArrival,executionTime, deadline, firstJob,], ['Arrival of a new job',"Execution time","deadlines", "arrival of the first job"])
	plt.show()

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

def main(filename, scheduler, start, end):
	newSystemList = readFile(filename)
	print(newSystemList)
	offsets, wcets, periods = getOffsetWCETPeriodLists(newSystemList)

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
	if(scheduler == "edf"):
		EDF(filename, start, end)
	else:
		LLF(filename, start, end)

if __name__ == "__main__":

	if(len(sys.argv) == 5):
		filename = sys.argv[1]
		scheduler = sys.argv[2]
		start = int(sys.argv[3])
		end = int(sys.argv[4])
		main(filename, scheduler, start, end)
	
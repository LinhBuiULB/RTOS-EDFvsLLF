import sys
import random
import copy
from math import gcd
import matplotlib.pyplot as plt
import numpy as np
import string
import pylab as P
import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerPatch

UPPER_BOUND_VALUE = 9999

##################################################
#               Parsing functions                #
##################################################

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



##################################################
#     EDF feasibility interval computation       #
##################################################

def LCM(numbers):
	"""
	Computing least common multiple
	"""
	lcm = numbers[0]
	for i in numbers[1:]:
	  lcm = lcm*i//gcd(lcm, i)
	return lcm

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
	print("0,{}".format(feasibilityIntervalUpperBound))



##################################################
#                System generator                #
##################################################

def matchRequiredUtilisationPercentage(wcets, periods, percentage, delta):
	"""
	Check whether or not we have our required utilisation percentage with the values generated randomly
	"""
	result = 0
	for i in range (0, len(wcets)):
		result += wcets[i]/periods[i]
	result = result * 100
	if ((percentage - delta) <= result <= (percentage + delta)):
		print("Utilization =",result)
		return True
	return False

def generateTasks(numberOfTasks, requiredUtilisationPercentage, delta):
	"""
	Generator of tasks 
	"""
	offsets = []
	for i in range(0, numberOfTasks):
		offsets.append(random.randint(0,2))

	loop = True
	while(loop):  #While we do not have our required utilisation percentage
		wcets = []
		periods = []
		count = 0
		while(count != numberOfTasks):
			for i in range (0, numberOfTasks):
				tempWcet = random.randint(1,50)
				tempPeriod = random.randint(1,50)
				if(tempWcet < tempPeriod):
					wcets.append(tempWcet)
					periods.append(tempPeriod)
					count = count + 1
					if(count == numberOfTasks):
						break
			if matchRequiredUtilisationPercentage(wcets, periods, requiredUtilisationPercentage, delta):
				loop = False
	return offsets, wcets, periods

def systemFileGenerator(offsets, wcets, periods,filename):
	"""
	Generator tasks in a file (question 2)
	"""
	file = open(filename, "w")
	for i in range(0, len(offsets)):
		file.write(str(offsets[i]) + "; " + str(wcets[i]) + "; " + str(periods[i]) + "\n")
	file.close()
	print("Your file {} has been succesfully generated".format(filename))



##################################################
#           EDF and LLF implementation           #
##################################################

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

def EDF(system, begin, end):
	"""
	EDF scheduling
	"""
	# Parse the system file 
	systemList = readFile(system)
	offsetList, wcetList, periodList = getOffsetWCETPeriodLists(systemList)

	# Initialization of variables 
	jobs = initJobsList(systemList)
	tasksDeadlinesDict = getTasksDeadlines(systemList, computeFeasibilityInterval(systemList), offsetList)
	tasksExecuted = []
	isJobDoneUntilNextDeadline = initIsJobDoneDict(systemList) # dict that allows us to get if the jobs are done for the current deadline 
	arrivalJob = copy.deepcopy(tasksDeadlinesDict)
	arrivalJobOutput = []
	preemptionsNb = 0

	if(isSchedulable):
		t = 0
		wcets = copy.deepcopy(wcetList) # This copy allows us to know when a job is finished (when WCET of the task = 0)

		while(t <= end):

			# Arrivals managament
			for deadlineList in arrivalJob.values():
				for deadline in deadlineList: 
					if(t == deadline):
						isJobDoneUntilNextDeadline[list(arrivalJob.keys())[list(arrivalJob.values()).index(deadlineList)]] = False
						arrivalJobOutput.append("{}:T{}J{}".format(t, list(arrivalJob.keys())[list(arrivalJob.values()).index(deadlineList)] , deadlineList.index(deadline) + 1 ))

			# Assign the current executing task 
			currentExecutedTask, smallest = getSmallestDeadlines(tasksDeadlinesDict, isJobDoneUntilNextDeadline)

			# Check if the deadline is missed 
			if isDeadlineMissed(smallest, t):
				tasksExecuted.append("Missed")
				break

			# Append the current executing task to the tasksExecuted and update wcets
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

		# Printing outputs in terminal and graphically 
		printOutputs(tasksExecuted, arrivalJobOutput, begin, end, systemList, preemptionsNb)
		printGraph(tasksExecuted, arrivalJob, offsetList, begin)

def LLF(system, begin, end):
	"""
	LLF scheduling
	"""
	# Parse the system file 
	systemList = readFile(system)
	offsetList, wcetList, periodList = getOffsetWCETPeriodLists(systemList)

	# Initialization of variables
	jobs = initJobsList(systemList)
	tasksDeadlinesDict = getTasksDeadlines(systemList, computeFeasibilityInterval(systemList), offsetList)
	tasksExecuted = []
	isJobDoneUntilNextDeadline = initIsJobDoneDict(systemList) # dict that allows us to get if the jobs are done for the current deadline 
	arrivalJob = copy.deepcopy(tasksDeadlinesDict)
	arrivalJobOutput = []
	preemptionsNb = 0

	# Laxity initialization
	laxityOfJobs = []
	CPUTimeUsed = [0 for i in range(len(jobs))]

	if(isSchedulable):
		t = 0
		wcets = copy.deepcopy(wcetList) # This copy allows us to know when a job is finished (when WCET of the task = 0)

		while(t <= end):

			# Arrivals managament
			for deadlineList in arrivalJob.values():
				for deadline in deadlineList: 
					if(t == deadline):
						isJobDoneUntilNextDeadline[list(arrivalJob.keys())[list(arrivalJob.values()).index(deadlineList)]] = False
						arrivalJobOutput.append("{}:T{}J{}".format(t, list(arrivalJob.keys())[list(arrivalJob.values()).index(deadlineList)] , deadlineList.index(deadline) + 1 ))

			# Computing of the laxities for every job 
			laxityOfJobs = computeLaxities(t, tasksDeadlinesDict, wcetList, isJobDoneUntilNextDeadline, CPUTimeUsed)

			# Assign the current executing task
			currentExecutedTask = laxityOfJobs.index(min(laxityOfJobs))

			# Compute preemption number
			if (t != 0):
				if tasksExecuted[t-1][0] != currentExecutedTask:
					if not isJobDoneUntilNextDeadline[tasksExecuted[t-1][0]]:
						preemptionsNb += 1 

			# Append the current executing task to the tasksExecuted and update wcets and CPUTimeUsed
			CPUTimeUsed[currentExecutedTask] += 1
			wcets[currentExecutedTask] -= 1 
			tasksExecuted.append((currentExecutedTask, jobs[currentExecutedTask]))

			# Check if the deadline is missed
			if(min(laxityOfJobs) < 0):
				tasksExecuted.append("Missed")
				break

			# If job done 
			if(wcets[currentExecutedTask] == 0):
				isJobDoneUntilNextDeadline[currentExecutedTask] = True
				jobs[currentExecutedTask] += 1
				wcets[currentExecutedTask] = wcetList[currentExecutedTask]
				tasksDeadlinesDict[currentExecutedTask] = tasksDeadlinesDict[currentExecutedTask][1:] 
				CPUTimeUsed[currentExecutedTask] = 0

			t += 1

		# Printing outputs in terminal and graphically
		printOutputs(tasksExecuted, arrivalJobOutput, begin, end, systemList, preemptionsNb)
		printGraph(tasksExecuted,arrivalJob, offsetList, begin)

def printOutputs(tasksExecuted, arrivalJobOutput, begin, end, systemList, preemptionsNb):
	"""
	Print the schedule of the system when the schedule is over
	"""
	print("Schedule from", begin, "to", end, ";", len(systemList), "tasks")

	i=0
	while(i < len(tasksExecuted)-1):
		interval = getTaskInterval(tasksExecuted, tasksExecuted[i][0], i)

		# Printing the executing jobs 
		if(i >= begin):
			print("{}-{} : T{}J{}".format(i, i+interval, tasksExecuted[i][0], tasksExecuted[i][1]))

		# Printing the arrival of jobs 
		for j in range(i+1, i+interval+1):
			for elem in arrivalJobOutput:
				if int(elem.split(":")[0]) == j:
					if(tasksExecuted[j] != "Missed"):
						print("{} : Arrival of job {}".format(j, elem.split(":")[1]))
		i+=interval

		# Stop printing if deadline missed 
		if (tasksExecuted[i] == "Missed"):
			print("{}: Job T{}J{} misses a deadline".format(i, tasksExecuted[-2][0], tasksExecuted[-2][1]))
			print("END: {} preemptions".format(preemptionsNb))
			break

def make_legend_arrow(legend, orig_handle,xdescent, ydescent,width, height, fontsize):
	"""
	Manage the arrow for the legend of the GUI 
	"""
	p = mpatches.FancyArrow(0, 0.5*height, width, 0, length_includes_head=True, head_width=0.75*height)
	return p

def printGraph(tasksExecuted, arrivalJob, offsetList, begin):
	"""
	Plotting the schedule graphically 
	"""

	x = []
	y = []
	xCircle = []
	yCircle = [] 
	plt.figure(figsize=(12,7)) 
	
	# Create two arrays for the execution time to be plotted
	missed = 0
	for i in range(begin, len(tasksExecuted)):
		if(tasksExecuted[i] != "Missed"):
			plt.text(i,tasksExecuted[i][0], str(tasksExecuted[i][1]), color = 'w', position =(i+0.5,tasksExecuted[i][0]))
			y.append(tasksExecuted[i][0])
			x.append(i)
		else:
			missed += 1
			plt.text(i,tasksExecuted[i-1][0], "Job missed !",ha="center", va="center",bbox=dict(boxstyle="round",ec=(1., 0.5, 0.5),fc=(1., 0.8, 0.8),))

	# Create two arrays for the deadlines to be plotted and draw the arrows corresponding to the arrival
	for i in range(len(arrivalJob)):
		for deadline in arrivalJob[i]:
			yCircle.append(i)
			xCircle.append(deadline)
			jobArrival  = plt.arrow(deadline,i-0.35,0,0.2, fc="k", ec="k", head_width = 0.5, head_length = 0.1)

	# Draw the first arrival of the job of each tasks
	for i in range(len(offsetList)):
		firstJob =plt.arrow(offsetList[i]+0.05,i-0.35,0,0.2,fc="g", ec="g", head_width = 0.5, head_length = 0.1, linewidth = 2)

	y = np.array(y)
	x = np.array(x)		
	xCircle = np.array(xCircle)
	yCircle = np.array(yCircle)
	deadline = plt.scatter(xCircle, yCircle, s=120, linewidth = 2,facecolors='none', edgecolors='red', zorder=1)

	ylabels = []
	xlabels = [] 

	countX = begin
	for j in range(begin, len(x)+begin+missed):
		xlabels.append(countX)
		countX += 1 
	
	xlabels = np.array(xlabels)
	
	countY = 0 
	for i in range(len(x)):
		ylabels.append(countY)
		countY += 1

	executionTime = plt.barh(y, [1]*len(x), left=x, color = 'blue', edgecolor = 'green', align='center', height=0.1, zorder = -1)

	plt.grid(color='black', linestyle='dotted', linewidth=1)
	plt.ylim(max(y)+0.5, min(y)-0.5)
	plt.xlim(min(x), max(x)+missed)
	plt.yticks(np.arange(y.max()+1), ylabels)
	plt.xticks(np.arange(begin,xlabels.max()+1), xlabels)
	plt.xlabel("t")
	plt.ylabel("Task number")
	plt.legend([jobArrival,executionTime, deadline,firstJob,], ['Arrival of a new job',"Execution time","deadlines", "Arrival of the first job"],handler_map={mpatches.FancyArrow : HandlerPatch(patch_func=make_legend_arrow),})
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
	"""
	Main function excuting EDF or LLF 
	"""
	newSystemList = readFile(filename)

	if(scheduler == "edf"):
		EDF(filename, start, end)
	else:
		LLF(filename, start, end)

if __name__ == "__main__":

	# Managing all arguments exceptions 

	# Manage question 1 arguments: printing of the feasibility interval
	if(len(sys.argv) == 3):
		intervalType = sys.argv[1]
		filename = sys.argv[2]
		if(intervalType == "edf_interval"):
			try:
				newSystemList = readFile(filename)
				feasibilityIntervalUpperBound = computeFeasibilityInterval(newSystemList)
				printFeasibilityInterval(feasibilityIntervalUpperBound)
			except IOError  as e:
				print("Cannot open {}".format(filename))
		else:
			print("Error : argument(s) incorrect.")

	elif(len(sys.argv) == 5):
		firstArg = sys.argv[1]
		secondArg = sys.argv[2]
		thirdArg = sys.argv[3]
		fourthArg = sys.argv[4]

		# Manage question 2 arguments : generator of tasks 
		if(firstArg == "gen"):
			try:
				numberOfTasks = int(secondArg)
				requiredUtilisationPercentage = int(thirdArg)
				delta = 2 #Margin of error accepted
				offsets, wcets, periods = generateTasks(numberOfTasks, requiredUtilisationPercentage, delta)
				systemFileGenerator(offsets, wcets, periods,fourthArg)
			except ValueError as e:
				print("Error : invalid value for the number of tasks or the pourcentage utilisation")
		
		# Manage question 3 arguments : EDF / LLF scheduling
		elif(firstArg == "edf" or firstArg == "llf"):
			try:
				scheduler = sys.argv[1]
				filename = sys.argv[2]
				start = int(sys.argv[3])
				end = int(sys.argv[4])
				if(start < end):
					main(filename, scheduler, start, end)
				elif(start == end):
					print("Error : the two values must be different")
				else:
					print("Error : the lower bound must be smaller than the upper bound")

			except ValueError as e:
				print("Error : invalid value for the bounds")
		else:
			print("Error : wrong arguments")

	else:
		if(len(sys.argv) > 5 ):
			print("Error : too much arguments")

		elif(len(sys.argv) != 3 and len(sys.argv) < 5 ):
			print("Error : missing argument(s)")

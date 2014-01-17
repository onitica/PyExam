import math
import time
import os
import re
#Some basic utility functions

def isemptystring(i):
	return not i or i.isspace()
	
############################## PARSING FUNCTIONS ####################################	
	
#Use this to sanitize params if they are paths (i.e. convert relative to absolute paths)
#Called for all params, but will only apply santization if the param is declared with format {f*}
def sanitize_if_filepath(param, var, relpath):
	regexp = re.compile('{f(.*)}')
	if var[0] != os.sep and regexp.match(param) and not relpath in var:
		return os.path.join(relpath, var)
	return var	

############################## ARRAY AGGREGATE FUNCTIONS ############################

#Return the first element of the array
def first(array):
	return array[0]

#Calculate the mean of a number array
def mean(array):
	return sum(array)/len(array)
	
def variance(array):
	m = mean(array)
	return mean(list(map(lambda x: x * x, map(lambda x: x - m, array))))

#Calculate the standard deviation of a number array
def std(array):	
	return math.sqrt(variance(array))
	
############################## TIMING FUNCTIONS ####################################

#Use time.time() instead of time.clock() since we are measuring work outside process
def get_current_time():
	return time.time()

def get_elapsed_time(t_):
	return time.time() - t_

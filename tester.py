import os
import subprocess
import argparse
import random
import formatter
import utils
import shell

#TODO: Handle params gracefully
# If no params for test_params or runtype_params handle them without crashing
# Assertions in parse_test_file

#Default Flags and constants
DEBUG = False
VERBOSE = False
COMMENT_DELIM = '#'

#Basic function logic for looping parsed file and doing tests
def trial_base(opts, func):
	results = []
	iterations = range(int(opts['iterations'])) if 'iterations' in opts else [0]
	
	for test in opts['tests']:
		test = test.strip()
		test_results = [test]
		for values in opts['values']:
			value_results = [values[0]]
			current_test = test
			runtype_params = []
			clean_command = opts['clean'] if 'clean' in opts else None
			for i, param in enumerate(opts['test_params']):
				current_test = current_test.replace(param, values[i])
				if('runtype_params' in opts and param in opts['runtype_params']):
					runtype_params.append(values[i])
				if(clean_command and (param in clean_command)):
					clean_command = clean_command.replace(param, values[i])
			if(VERBOSE):
				print('Testing:', current_test)
			for iteration in iterations:
				value_results.append(func(
				{ 'test' : current_test,
				'params' : runtype_params,
				'values' : values,
				'iteration' : iteration }))
			clean_test(clean_command)
			test_results.append(value_results)
		results.append(test_results)
	
	if(DEBUG):
		assert len(results) == len(opts['tests']), "Failed generating results for all tests!"

	return results	

#Each test get an opts dictionary that contains the following:
#test - Text signifying the test to execute
#values - The value paramaters subbed into the command
#iteration - The iteration of the test
def test_speed(opts):
	t = utils.get_current_time()
	shell.call(opts['test'])
	return utils.get_elapsed_time(t)

def speed_trial(opts):
	return trial_base(opts, test_speed)
	
def test_size(opts):
	shell.call(opts['test'])
	return os.path.getsize(opts['params'][0])
	
def size_trial(opts):
	return trial_base(opts, test_size)
	
def test_debug(opts):
	return random.randint(0,100)
	
def debug_trial(opts):
	return trial_base(opts, test_debug)

def clean_test(command):
	if command:
		if(VERBOSE):
			print('Cleaning with command:',command)
		shell.call(command)

#define test file parameters
vmulti_params = ['values', 'tests'] #paramaters that can have multiple arguments on lines
vsingle_params = ['iterations', 'runtype', 'output', 'clean'] #paramters that only take a single value -> will throw error if they have more than one
delim_params = ['values', 'output', 'test_params', 'runtype_params'] #parameters that are delimited by the delim character
delim_char = ';' #the delim character for array params
def parse_test_file(filepath):
	#Read file, stripping whitespace on lines and removing empty lines		
	f = open(filepath)
	lines = [i for i in [str(l).partition(COMMENT_DELIM)[0] for l in f.readlines()] if utils.isemptystring(i) == False]
	f.close()

	#Variables for parsing
	current = 'none'
	lcount = 0
	results = {}
	for param in vmulti_params:
		results[param] = []

	#Basic file parsing			
	while (len(lines) > 0):
		lcount += 1
		front = lines.pop(0)
		if(':' in front):
			current,val = [f.strip() for f in front.split(':')]
			if current in vmulti_params:
				if not utils.isemptystring(val):
					results[current].append(val)
				continue
			if utils.isemptystring(val):
				results[current] = lines.pop(0).strip()
			else:
				results[current] = val
		elif(current in vmulti_params):
			results[current].append(front)
		else:
			raise Exception('Error parsing at line ' + str(lcount))
	
	#Parse delim params into arrays
	for param in delim_params:
		if param in results:
			if param in vmulti_params:
				results[param] = list(map(lambda s: [st.strip() for st in s.split(delim_char)], results[param]))
			else:
				results[param] = [st.strip() for st in results[param].split(delim_char)]
			
	#TODO: Assert here that length of all values arrays are equal to test_param arrays
	
	#Get relative filepath from current dir to test
	relpath = filepath.split(os.sep)
	relpath.pop()
	relpath = os.sep.join(relpath)
	
	#If passing filepath params -> Convert relative paths to absolute paths
	for i, param in enumerate(results['test_params']):
		for values in results['values']:
			values[i] = utils.sanitize_if_filepath(param, values[i], relpath)			
			
	return results

def file_arg (string):
	if os.path.isfile(string):
	        return string
	else:
	        raise argparse.ArgumentTypeError('The input must be a file')

parser = argparse.ArgumentParser()
parser.add_argument('testfile', type=file_arg, help='The test file to test')
parser.add_argument('--verbose', action='store_true', help='Write output as running if verbose')
parser.add_argument('--debug', action='store_true', help='Run assert statements to test the program')
parser.add_argument('-o', help='specify the output file. Default will be of format pyexam_output.<format_type_chosen>')
args = parser.parse_args()

VERBOSE = args.verbose
DEBUG = args.debug
if(VERBOSE): 
	print('Running your favorite testing framework...')

opts = parse_test_file(args.testfile)

if(VERBOSE): 
	print('Running:', opts['runtype'] + '_trial')
	
if(args.o):
	f = open(args.o, 'w')
else:
	f = open('pyexam_output.csv', 'w')

test_results = vars()[opts['runtype'] + '_trial'](opts)
formatter.outputCSV(f, opts['output'], test_results)

f.close()
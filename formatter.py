import builtins
import utils

#formatter for displaying test results
def outputCSV(f, output_list, results):
	print(','.join(output_list), file=f)
	for res in results:
		command = res.pop(0)
		for value_res in res:
			output_dict = generate_output_dict(output_list, command, value_res.pop(0), value_res)
			print(','.join([str(output_dict[i]) for i in output_list]), file=f)
	
#Data wrappers for generate_output_dict
var_wrappers = ['command', 'value']
builtins_func_wrappers = ['min', 'max']
utils_func_wrappers = ['std', 'mean', 'first']

#Generate a dictionary of values to output 
#We add this step because we may format this dictionary in different ways
def generate_output_dict(output_list, command, value, results):
	res = {}
	for output in output_list:
		if output in var_wrappers:
			res[output]  = vars()[output]
		elif output in builtins_func_wrappers:
			res[output] = getattr(builtins, output)(results)
		elif output in utils_func_wrappers:
			res[output] = getattr(utils, output)(results)
		else:
			raise Exception('Output ' + output + ' is not supported!')
	return res
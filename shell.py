import subprocess
import os
import re

# This module will attempt to read your default shell profile for aliases
# This can be used to figure out aliases for use with subprocess

# Will only parse basic aliases for sh and bash, but with zsh will also parse globals

shell_profile_dict = { 'sh' : ['.profile'], 'zsh' : ['.zshrc'], 'bash' : ['.bash_profile', '.bashrc'] }
parsed_reg_aliases = None
parsed_global_aliases = None

def determine_default_shell():
	return os.environ['SHELL'].split(os.sep).pop()

def determine_home():
	return os.environ['HOME'].strip()

def read_shell_profile():
	global parsed_reg_aliases
	global parsed_global_aliases
	try:
		s = determine_default_shell()
		h = determine_home()
		parsed_reg_aliases = {}
		parsed_global_aliases = {}
		value_parser = re.compile('(?P<alias>[^\']+)=\'(?P<value>[^\']+)\'')
		
		for prof in shell_profile_dict[s]:
			with open(os.path.join(h,prof)) as prof_file:
				lines = [l.strip() for l in prof_file.readlines()] 
				regexp = re.compile('alias (?P<value>.+)')
				for l in lines:
					parsed = regexp.match(l)
					if parsed:
						check_flag_partition = parsed.group('value').partition(' ')
						
						#Check for flags - parse global and ignore all other
						if '-' in check_flag_partition[0]:
							if check_flag_partition[0] == '-g':
								parse_key_values_into_dict(check_flag_partition[2], value_parser, parsed_global_aliases)
							else:
								print('ERROR: Unknown alias flag:', tokens[0])
						else: #Parse regular alias tokens
							parse_key_values_into_dict(parsed.group('value'), value_parser, parsed_reg_aliases)
	except:
		print("Shell.py: Unable to parse profile!");
		return None
		
def parse_key_values_into_dict(val, parser, insertion_dict):
	parsed_vals = parser.findall(val)
	for matches in parsed_vals:
		insertion_dict[matches[0].strip()] = matches[1]
	
def fix_aliases(fullcommand):
	global parsed_reg_aliases
	global parsed_global_aliases
	if not parsed_reg_aliases:
		read_shell_profile()
		
	shell_type = determine_default_shell()
	print(parsed_global_aliases)
	print(parsed_reg_aliases)
	
	tokens = fullcommand.split(' ')
	print(tokens)
	if parsed_reg_aliases:
		if tokens[0] in parsed_reg_aliases:
			tokens[0] = parsed_reg_aliases[tokens[0]]
	
	if shell_type == 'zsh' and parsed_global_aliases:
		for i, token in enumerate(tokens):
			if token in parsed_global_aliases:
				tokens[i] = parsed_global_aliases[token]
		
	return ' '.join(tokens)
	
def call(command):
	subprocess.call(fix_aliases(command), shell=True)
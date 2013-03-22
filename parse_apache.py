#!/usr/bin/python
import re
import os
log_file = open("access_log_1","r")
regex = '([(\d\.)]+) - - \[(.*?)\] "(.*?)" (\d+) ((\d+)|-) ("-")?(.*?) "(.*?)"'

for line in log_file.readlines():
	try:
		search = re.match(regex, line).groups()[5]
	except :
		print line 

#!/usr/bin/python
import re
import os
import dateutil.parser 

for i in range(1,5):
	log_file = open("access_log_"+str(i),"r")
	regex = '([(\da-zA-Z:\.\-)]+) - - \[(.*?)\] "(.*?)" (\d+) ((\d+)|-) ("-")?(.*?) "(.*?)"'
	print i
	for line in log_file.readlines():
		try:
			search = re.match(regex, line).groups()
			dateutil.parser.parse(search[1].replace(':', ' ', 1))
		except :
			print line 

#!/usr/bin/python
import re
import os
import dateutil.parser
from datetime import datetime
from pymongo import MongoClient

class LogAnalysis:
	def __init__(self):
		self.client = MongoClient()
		self.db = self.client.project_test
	def log_insert(self, collection_name, date):
		collection = self.db[collection_name]
		collection.insert(date)
	def read_apache_logs(self):
		fileds = ['clien_ip','date','request','status','request_size','browser_string']
		for i in range(1,5):
			log_file = open("access_log_"+str(i),"r")
			regex = '([(\da-zA-Z:\.\-)]+) - - \[(.*?)\] "(.*?)" (\d+) ((\d+)|-) ("-")?(.*?) "(.*?)"'
			print i
			for line in log_file.readlines()[:20]:
				try:
					search = re.match(regex, line).groups()
					date = dateutil.parser.parse(search[1].replace(':', ' ', 1))
					date = (datetime(date.year,date.month,date.day,date.hour,date.minute,date.second),)
					path = (search[2].split()[1],)
					log_data = dict(zip(fileds,search[:1]+date+path+search[3:5]+search[8:]))
					self.log_insert('access_log',log_data)
				except :
					print line
la = LogAnalysis()
la.read_apache_logs()
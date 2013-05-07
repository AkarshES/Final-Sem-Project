import re
import calendar
from pymongo import MongoClient
from datetime import datetime
from log_analyzer import LogAnalyzer

class SysLogFileProcessor:
	"""This class reads a syslog file and stores the log information into a database"""
	def __init__(self, db = 'test'):
		self.client = MongoClient()
		self.db = self.client[db]
	
	def log_insert(self, collection_name, data):
		collection = self.db[collection_name]
		collection.insert(data)

	def load_syslog_data_into_DB(self, logfile, collection_name):
		logfile = open(logfile,'r')
		month_dict = {v: k for k,v in enumerate(calendar.month_abbr)}
		count = 0
		log_list = []
		fields = ['date', 'service', 'time_since_bootup', 'message']
		for line in logfile.readlines()[50:]:
			try:
				list = []
				data = re.search("([A-z]+)  (\d+) (\d+:\d+:\d+) ([^ ]+) ([^ \[\]:]+)(\[(\d+)\])?: \[?([0-9. ]+)?\]?(.*)",line).groups()
				date = datetime(datetime.now().year,month_dict[data[0]],int(data[1]),int(data[2][:2]),int(data[2][3:5]),int(data[2][6:]))
				time_since_bootup = None
				if data[7] is not None:
					time_since_bootup = data[7].lstrip()
				message = data[8].lstrip()
				data_dict = dict(zip(fields,[date]+[data[4]]+[time_since_bootup]+[message]))
				log_list.append(data_dict)
				if count == 400:
					count = 0
					self.log_insert(collection_name,log_list)
					log_list = []
				count += 1
			except: 
				print line

class SysLogAnalyzer(LogAnalyzer):
	def __init__(self, db = 'test', collection = 'None', from_date = None, to_date = None):
		LogAnalyzer.__init__(self, db, collection, from_date, to_date)
		self.log_fields = ['date', 'service', 'time_since_bootup', 'message']
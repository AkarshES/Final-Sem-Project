#!/usr/bin/python
import re
import os
import dateutil.parser
from datetime import datetime
from pymongo import MongoClient
from pandas import DataFrame

class LogAnalysis:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.project_test
    
    def log_insert(self, collection_name, data):
      collection = self.db[collection_name]
      collection.insert(data)

    def process_apache_log_file(self, file_name, collection_name):
        """
        Reads the log data from 'file_name' and loads it into 'collection_name' in MongoDB
        """
        fields = ['client_ip','date','request','status','request_size','browser_string']
        apache_log_regex = '([(\da-zA-Z:\.\-)]+) - - \[(.*?)\] "(.*?)" (\d+) ((\d+)|-) ("-")?(.*?) "(.*?)"'
        log_file = open(file_name,"r")
        for line in log_file.readlines():
            try:
                search = re.match(apache_log_regex, line).groups()
                date = dateutil.parser.parse(search[1].replace(':', ' ', 1))
                date = (datetime(date.year,date.month,date.day,date.hour,date.minute,date.second),)
                path = (search[2].split()[1],)
                log_data = dict(zip(fields,search[:1]+date+path+search[3:5]+search[8:]))
                if(log_data['request_size'] == '-'):
                    log_data['request_size'] = 0
                self.log_insert(collection_name,log_data)
            except :
                print line

    def load_apache_logs_into_DataFrame(self, collection_name):
        fields = ['client_ip','date','request','status','request_size','browser_string']
        collection = self.db[collection_name]
        log_data = collection.find()
        return DataFrame(list(log_data),columns = fields)


    def median(self, collection_name, mean_of, groupby = None):
        log_data = self.load_apache_logs_into_DataFrame(collection_name)
        computed_mean = None
        try:
            if(groupby):
                computed_mean = log_data[mean_of].groupby(log_data[groupby]).median()
            else:   
                computed_mean = log_data[mean_of].median()
        except KeyError:
            print 'Check if the field ' + mean_of + ' exists.'
        return computed_mean

    def date_query(self, collection_name):
        df = self.load_apache_logs_into_DataFrame(collection_name)
        print df['request_size'].groupby([df['date'].map(lambda x: (x.month, x.day)),df['status']]).median()

if __name__ == '__main__':
    la = LogAnalysis()
    la.date_query('access_log_1')
    #la.process_apache_log_file('access_log_1','access_log_1')
    #print la.median('access_log_1','request_size')
    #print la.median('access_log_1','request_size','status')                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
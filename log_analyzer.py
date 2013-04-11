#!/usr/bin/python
import re
import os
import dateutil.parser
from datetime import datetime
from pymongo import MongoClient
from pandas import DataFrame

class LogParser:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.project_test
    
    def log_insert(self, collection_name, data):
      collection = self.db[collection_name]
      collection.insert(data)

    def load_apache_log_file_into_DB(self, file_name, collection_name):
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
class LogAnalyzer:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.project_test

    def load_apache_logs_into_DataFrame(self, collection_name):
        fields = ['client_ip','date','request','status','request_size','browser_string']
        collection = self.db[collection_name]
        log_data = collection.find()
        return DataFrame(list(log_data),columns = fields)

    def median(self, df, mean_of, group_by = None):
        computed_mean = None
        try:
            if(group_by):
                computed_mean = df[mean_of].groupby(df[group_by]).median()
            else:   
                computed_mean = df[mean_of].median()
        except KeyError:
            print 'Check if the field ' + mean_of + ' exists.'
        return computed_mean

    def group_by_date(self, df):
        return df.groupby([df['date'].map(lambda x: (x.year, x.month, x.day)),df['status']])

    def count(self, df, field):
        return df[field].count()

if __name__ == '__main__':
    # la = LogAnalyzer()
    # df = la.load_apache_logs_into_DataFrame('access_log_1')
    # df = la.group_by_date(df)
    # print la.count(df, 'request_size')
    # print la.median(df, 'request_size')
    lp = LogParser()
    lp.load_apache_log_file_into_DB('access_log_2','access_log_2')
    #print la.median('access_log_1','request_size')
    #print la.median('access_log_1','request_size','status')
#!/usr/bin/python
import re
import os
import io
import json
import dateutil.parser
from datetime import datetime
from pymongo import MongoClient
from pandas import DataFrame
# import pandasjson

class LogParser:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.test
    
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
                return False
        return True

class LogAnalyzer:    
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.test

    def load_apache_logs_into_DataFrame(self, collection_name):
        fields = ['client_ip','date','request','status','request_size','browser_string']
        if collection_name not in self.db.collection_names():
            return False
        collection = self.db[collection_name]
        log_data = collection.find().limit(50)
        return DataFrame(list(log_data),columns = fields)

    def get_log_data(self, collection_name):
        fields = ['client_ip','date','request','status','request_size','browser_string']
        if collection_name not in self.db.collection_names():
            return False
        collection = self.db[collection_name]
        log_data = collection.find().limit(50)
        log_list = []
        for log in log_data:
            log_list.append(log)
            log['date'] = log['date'].strftime("%I:%M%p on %B %d, %Y")
            log.pop('_id')
        return json.dumps({"data" : log_list})

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
    
    def group_by(self, df, field):
        return df.groupby(df[field])
    
    def count_hits(self, collection_name):
        df = self.load_apache_logs_into_DataFrame(collection_name)
        if df is False:
            return False
        df = self.group_by_date(df)
        count_data = self.count(df, 'request_size')
        counts_list = []
        for row in count_data.index:
            counts_list.append({"date" : datetime(row[0][0],row[0][1],row[0][2]).strftime("%s"), "status" : row[1], "count" : str(count_data[row])})
        return json.dumps({"data" : counts_list})
        # json_data = pandasjson.to_json(self.count(df, 'request_size'))
        # json_load = json.loads(json_data)
        # new_json_dict = []
        # for row in json_load:
        #     row_list = json.loads(row)
        #     new_json_dict.append({'date': datetime(row_list[0][0],row_list[0][1],row_list[0][2]).strftime("%s"), 'status':row_list[1], 'count' : json_load[row]})
        # return json.dumps({"data": new_json_dict})

if __name__ == '__main__':
    # lp = LogParser()
    # lp.load_apache_log_file_into_DB('access_log_3','access_log_3')
    la = LogAnalyzer()
    print la.get_log_data('access_log_1')
    # print la.count_hits('access_log_1')

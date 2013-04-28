#!/usr/bin/python
import re
import os
import io
import json
import dateutil.parser
from datetime import datetime
from pymongo import MongoClient
from pandas import DataFrame
from referer_parser import Referer
from ua_parser import user_agent_parser
import pygeoip
class LogParser:
    def __init__(self, db = 'test'):
        self.client = MongoClient()
        self.db = self.client[db]
        self.geoip = pygeoip.GeoIP('./GeoIP.dat', pygeoip.MEMORY_CACHE) # change the path on your machine. get it from http://dev.maxmind.com/geoip/install/country
    
    def log_insert(self, collection_name, data):
      collection = self.db[collection_name]
      collection.insert(data)

    def load_apache_log_file_into_DB(self, file_name, collection_name):
        """
        Reads the log data from 'file_name' and loads it into 'collection_name' in MongoDB
        """
        fields = ['client_ip','date','request','status','request_size','browser_string','device' ,'os','browser','referer', 'request_country']
        apache_log_regex = '([\da-zA-Z:\.\-]+) - - \[(.*?)\] "(.*?)" (\d+) ((\d+)|-) ("-")?(.*?) "(.*?)"'
        compiled_apache_log_regex = re.compile(apache_log_regex)
        log_file = open(file_name,"r")
        count = 0
        log_list = []
        for line in log_file.readlines():
            try:
                search = compiled_apache_log_regex.match(line).groups()
                date = dateutil.parser.parse(search[1].replace(':', ' ', 1))
                date = (datetime(date.year,date.month,date.day,date.hour,date.minute,date.second),)
                path = (search[2].split()[1],)
                log_data = dict(zip(fields,search[:1]+date+path+search[3:5]+search[8:]))
                if(log_data['request_size'] == '-'):
                    log_data['request_size'] = 0
                else:
                    log_data['request_size'] = paserint(log_data['request_size'])
                log_data.update(self.extract_user_agent_info(log_data['browser_string']))
                request_country = self.geoip.country_name_by_addr(search[0])
                log_data.update({'request_country' : request_country})
                count += 1
                log_list.append(log_data)
                if count == 400:
                    count = 0
                    self.log_insert(collection_name,log_list)
                    log_list = []
            except :
                print line
                #return False
        if len(log_list) > 0:
            self.log_insert(collection_name,log_list)
        return True

    def extract_user_agent_info(self, ua_string):
        result_dict = user_agent_parser.Parse(ua_string)
        referer_url = re.search("(?P<url>https?://[^\s]+)", ua_string)
        ua_info_dict = {'device' : result_dict['device']['family'],'os' : result_dict['os']['family'], 'browser' : result_dict['user_agent']['family']}
        if referer_url is not None:
            ua_info_dict['referer'] = Referer(referer_url.group("url")).uri[1]
        return ua_info_dict

class CollectionNotFound():
    pass

class LogAnalyzer:    
    def __init__(self, db = 'test', collection = 'None'):
        self.client = MongoClient()
        self.db = self.client[db]
        if collection not in self.db.collection_names():
            raise CollectionNotFound("The given collection was not found in the DB.")
        self.collection = self.db[collection]
        self.log_fields = ['client_ip','date','request','status','request_size','browser_string','device' ,'os','browser','referer', 'request_country']

    def load_apache_logs_into_DataFrame(self):
        log_data = self.collection.find()
        return DataFrame(list(log_data),columns = self.log_fields)

    def get_log_data(self, collection_name, from_date = None, to_date = None, page_number = 0):
        if from_date is None:
            from_date = datetime(1970,1,1)
        if to_date is None:
            to_date = datetime.now()
        if collection_name not in self.db.collection_names():
            return False
        collection = self.db[collection_name]
        log_data = collection.find({'date' : {"$gte": from_date, "$lt" : to_date}})
        page_count = log_data.count()
        log_data = log_data.skip(page_number * 50).limit(50)
        log_list = []
        for log in log_data:
            log_list.append(log)
            log['date'] = log['date'].strftime("%s")
            log.pop('_id')
        return {"data" : log_list, "max_page" : page_count}

    def get_log_date_range(self):
        min = self.collection.find().sort([("date", 1)]).limit(1)
        max = self.collection.find().sort([("date", -1)]).limit(1)
        return {"min_date" : min[0]['date'].strftime("%s"),"max_date" : max[0]['date'].strftime("%s")}


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
    
    def generate_stats(self):
        stats_dict = {}
        stats_dict['date_range'] = self.get_log_date_range()

    def to_dict(self, data, field = 'key', operation = ''):
        data_list = []
        for row in data.index:
            data_list.append({field : row, operation : data[row]})
        return {"data" : data_list}

    def count_hits(self, collection_name):
        df = self.load_apache_logs_into_DataFrame(collection_name)
        if df is False:
            return False
        df = self.group_by_date(df)
        count_data = self.count(df, 'request_size')
        counts_list = []
        for row in count_data.index:
            counts_list.append({"date" : datetime(row[0][0],row[0][1],row[0][2]).strftime("%s"), "status" : row[1], "count" : str(count_data[row])})
        return {"data" : counts_list}
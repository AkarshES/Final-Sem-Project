from log_analyzer import LogAnalyzer
if __name__ == '__main__':
    # lp = LogParser()
    # lp.load_apache_log_file_into_DB('access_log_1','access_log')
    # lp.load_apache_log_file_into_DB('access_log_2','access_log')
    # lp.load_apache_log_file_into_DB('access_log_3','access_log')
    # lp.load_apache_log_file_into_DB('access_log_4','access_log')
    la = LogAnalyzer(db = 'test', collection = 'Akarsh_rpr2')
    # print la.get_log_data(collection_name = 'access_log', page_number = 5)
    # print la.get_log_data('access_log')
    # print la.count_hits('access_log')
    
    df = la.load_apache_logs_into_DataFrame()
    data = la.group_by(df,['request_country'])
    la.daily_bandwidth_sums()
    # print la.sum(data, 'request_size')
    # print (la.count(data, ['request_country'])['request_country']) #group_by os and browser and return the count of referer based on that groups. notice the field selection after the count, otherwise all the fields will be printed
    # print la.count(data, 'referer')
    # data = la.group_by(df, 'referer')
    # data = la.count(data, 'referer')
    # print la.to_dict(data)
    # #print la.to_dict(data, 'referer', 'count')
    # data = la.group_by(df, 'os')
    # data = la.count(data, 'os')
    # print data
    # data = la.group_by(df, 'request_country')
    # data = la.count(data, 'request_country')
    # print data
    # data = la.group_by(df, 'browser')
    # data = la.count(data, 'browser')
    # print data
    # data = la.group_by(df, 'device')
    # data = la.count(data, 'device')
    # print data
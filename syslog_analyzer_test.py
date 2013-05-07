# from syslog_analyzer import SysLogFileProcessor
# slp = SysLogFileProcessor()
# slp.load_syslog_data_into_DB('/var/log/syslog','syslog_1')
from syslog_analyzer import SysLogAnalyzer

sla = SysLogAnalyzer(collection = 'syslog_1') 
df = sla.load_apache_logs_into_DataFrame()
data = sla.group_by(df, ['service','message'])
print sla.count(data, 'message')

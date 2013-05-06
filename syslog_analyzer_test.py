from syslog_analyzer import SysLogFileProcessor
sla = SysLogFileProcessor()
sla.load_syslog_data_into_DB('/var/log/syslog','syslog_1')
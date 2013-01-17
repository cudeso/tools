#!/usr/bin/env python
# encoding: utf-8

import apachelog, sys
import MySQLdb

def apache_2_sql ( logfile ):
	"Convert apache logfile to mysql table"
	
	p = apachelog.parser(apachelog.formats['extended'])
	for line in open( logfile ):
	 try:
	  data = p.parse(line)
	 except:
		sys.stderr.write("Unable to parse %s" % line)
	 converted_date = apachelog.parse_date(data['%t'])
	 converted_request = data['%r'].lower().strip()

	 print data
	return
	
conn = MySQLdb.connect (host = "localhost",user = "apache_log", db = "apache_log")
cursor = conn.cursor()

apache_2_sql( 'access_log' )
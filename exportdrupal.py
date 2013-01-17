#!/usr/bin/env python
# encoding: utf-8
"""
extractdrupal.py

Export Drupal tables from field_revision_body

Created by Koen Van Impe on 2013-01-17.
Copyright (c) 2013 cudeso.be. All rights reserved.
"""

import sys
import os
import MySQLdb
import subprocess
import re

d_host = "localhost"
d_user = ""
d_passwd = ""
d_db = ""
basepath = '/tmp/extractdrupal/'

conn = MySQLdb.connect (host = d_host,user = d_user, passwd = d_passwd , db = d_db)
cursor = conn.cursor()

def exportdrupal ( query ):	
	c = cursor.execute( query )
	
	while True:
		row = cursor.fetchone()
		if row is None:
			break
		title = re.sub(r'\s', '', row[0])
		title = re.sub(r'[^a-zA-Z0-9: ]', '', title)
		filename = basepath + title + "_nid_" + str(row[2]) + "_vid_" + str(row[3]) + ".html"
		body = "<html>\n<head>\n<title>" + row[0] + "</title>\n<meta name=\"drupal-nid\" content=\"" + str(row[2]) + "\">\n<meta name=\"drupal-vid\" content=\"" + str(row[3]) + "\">\n</head>\n\n<body>\n" + row[1] + "\n</body>\n\n</html>\n"
		export_file = open( filename , "w" )
		export_file.write( body )
		export_file.close()
	conn.commit()
	
exportdrupal( "	select node_revision.title, field_revision_body.body_value, node_revision.nid, node_revision.nid, node_revision.vid from node_revision, field_revision_body where node_revision.nid = entity_id ") 
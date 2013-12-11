#!/usr/bin/env python
#
# tiny Web Url Scanner
#
# Scan a website for the presence of URL resources and have the output comma separated displayed
# 
#  Koen Van Impe on 2013-12-11
#   koen dot vanimpe at cudeso dot be
#   license New BSD : http://www.vanimpe.eu/license
#

import sys
import urllib2
import argparse

parser = argparse.ArgumentParser(description='Tiny Web Url Scanner',epilog='Koen Van Impe - koen dot vanimpe at cudeso dot be', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('url', help='The URL to scan (include http://)')
parser.add_argument('-r', '--resources', help="File containing the resources to check", default="twus.input")
parser.add_argument('-v', '--verbose', help="Add verbose output", action="store_true", default=False)  

args = parser.parse_args()

base_url = args.url
web_resources = args.resources

if not base_url[-1:] == "/":
  base_url += "/"

try:
  file = open( web_resources , 'r')
  if args.verbose:
    print "Start scanning"
    print " Base URL: %s \n" % base_url
    print "\"Code\", \"URL\", \"Server\", \"Last Modified\", \"Content Type\", \"Cache Control\""
  for line in file:
    line = line.rstrip('\n')
    if line[:1] == "/":
      line = line.lstrip("/")
      
    check_url = base_url + line
    http_last_modified = ""
    http_server = ""
    http_content_type = ""
    http_cache_control = ""
    try:
      t = urllib2.urlopen( check_url )
      returncode = t.getcode()
      info = t.info()
      if "Server" in info:
        http_server = info["Server"]
      if "Last-Modified" in info:
        http_last_modified = info["Last-Modified"]
      if "Content-Type" in info:
        http_content_type = info["Content-Type"]
      if "Cache-Control" in info:
        http_cache_control = info["Cache-Control"]        
    except urllib2.HTTPError as e:
      returncode = e.code
    print "\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\"" % ( returncode , check_url, http_server, http_last_modified, http_content_type, http_cache_control)
  if args.verbose:
    print "\nScan finished"
except IOError:
  print "Unable to read the file with the web resources : %s " % web_resources

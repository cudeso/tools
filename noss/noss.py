#!/usr/bin/env python
#
# NMAP Open Service Scan
#
# Scan your network for open resolvers (or any other network service)
#  (nmap to sqlite inspired by nmapdb - Patroklos Argyroudis)
# 
# A script that reads an NMAP XML file, processes live hosts with open ports
# and stores the data in sqlite. A report afterwards lists the new
# open resolvers. Initially built for open resolvers but it can also used
# for any service that's detectably by an NMAP script
#
#  Koen Van Impe on 2013-12-01
#       v 0.2       2014-08-01
#       v 0.3       2014-08-06
#   koen dot vanimpe at cudeso dot be
#   license New BSD : http://www.vanimpe.eu/license
#
#
#


import sys
import os
#import xml.dom.minidom
import datetime, time
import sqlite3
import argparse
from commands import getstatusoutput
from lxml import etree

DATABASE = "noss.db"
DATABASE_SQL = "noss.sql"
APP_NAME = "NMAP Open Service Scan"
APP_VERSION = "0.3"
DEFAULT_NMAP = "noss"
DEFAULT_NMAP_XML = DEFAULT_NMAP + ".xml"
DEFAULT_CLEANUPS = 5
DEFAULT_SCAN_TARGET="127.0.0.1"
DEFAULT_SCAN_WITHOUT_PING=" -PN "
#NMAP_LOCATION="/usr/bin/nmap"
NMAP_LOCATION="/usr/local/nmap/bin/nmap"

HTTP_USER_AGENT="Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"

'''
 Main function, parse the app arguments
'''
def main():
  
  global conn, cursor
  
  parser = argparse.ArgumentParser('parser', description='Scan and report the open resolvers (or any other network service) in your network.', epilog='Koen Van Impe - koen.vanimpe@cudeso.be', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  
  parser.add_argument('-d', '--database' , help="Database to use", default=DATABASE)
    
  subparsers = parser.add_subparsers(title='Command switches', description='NOSS has a couple of command switches that tell it what you want it to do', dest='action')

  parser_import = subparsers.add_parser('import', help='Import data from external sources (NMAP)')
  parser_scan = subparsers.add_parser('scan', help='Launch a scan (NMAP)')
  parser_report = subparsers.add_parser('report', help='Build different reports')
  parser_stats = subparsers.add_parser('stats', help='Return statistics on the content of the database')
  parser_clean = subparsers.add_parser('clean', help='Clean the database')
  parser_init = subparsers.add_parser('init', help='Initialize the database')
  parser_empty = subparsers.add_parser('empty', help='Empty the database')
        
  parser_import.add_argument('-n', '--nmap-xml', help="The NMAP XML import file", default=DEFAULT_NMAP_XML)

  parser_clean.add_argument('-c', '--cleanups', help="Remove the older session data", default=DEFAULT_CLEANUPS, type=int, nargs="?")

  parser_report.add_argument('-s', '--sessions', help="Return the number of sessions", action="store_true", default=False)
  parser_report.add_argument('-l', '--sessions-list', help="List the sessions", action="store_true", default=False)
  parser_report.add_argument('-L', '--sessions-list-detail', help="List the sessions, with script-id", action="store_true", default=False)
  parser_report.add_argument('-D', '--sessions-dump', help="Print all the sessions", action="store_true", default=False)  
  parser_report.add_argument('-S', '--sessions-detail', help="Dump raw details of a session", type=int, default=False, nargs="?")
      
  parser_report.add_argument('-rh', '--report-history', help="Include the history in a report", action="store_true", default=False)
  parser_report.add_argument('-rd', '--report-dns', help="Report on open DNS resolvers", action="store_true", default=True)
  parser_report.add_argument('-rz', '--report-dns-zone', help="Report on DNS resolvers allowing zone transfers", action="store_true", default=False) 
  parser_report.add_argument('-rt', '--report-ntp', help="Report on open NTP servers", action="store_true", default=False)
  parser_report.add_argument('-rp', '--report-http', help="Report on open HTTP servers", action="store_true", default=False)  
  parser_report.add_argument('-rsh', '--report-snmp-header', help="Report all the SNMP headers", action="store_true", default=False)
  parser_report.add_argument('-ra', '--report-all', help="Report on all ports", action="store_true", default=False)  
  parser_report.add_argument('-rs', '--report-session', help="Report on this session", type=int)
  parser_report.add_argument('-rq', '--report-quick', help="Quick report (hostname + timestamp)", action="store_true", default=False)
  parser_report.add_argument('-rc', '--report-csv', help="Report with data in CSV format", action="store_true", default=False)
  
  parser_scan.add_argument('-sd', '--scan-dns', help="Scan for open DNS resolvers", action="store_true", default=False)
  parser_scan.add_argument('-sz', '--scan-dns-zone', help="Scan for DNS resolvers allowing zone transfers", action="store_true", default=False)
  parser_scan.add_argument('-sn', '--scan-snmp', help="Scan for SNMP servers'", action="store_true", default=False)
  parser_scan.add_argument('-st', '--scan-ntp', help="Scan for NTP servers'", action="store_true", default=False)  
  parser_scan.add_argument('-sh', '--scan-http', help="Scan for HTTP servers", action="store_true", default=False)
  parser_scan.add_argument('-sH', '--scan-http-headers', help="Scan for headers HTTP servers", action="store_true", default=False)
  parser_scan.add_argument('-t', '--scan-target', help="Target to scan", default=DEFAULT_SCAN_TARGET)    
  parser_scan.add_argument('-ti', '--scan-target-input-file', help="Target to scan (inputfile)", default=False)    
  parser_scan.add_argument('-o', '--output-file', help="The NMAP export base filename", default=DEFAULT_NMAP)
    
  printHeader()

  if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)
  args=parser.parse_args()  
  
  db = DATABASE
  if args.database is not None:
    db = args.database

    if args.action == "init":
      try:
        sql = open( DATABASE_SQL, "r").read() 
        conn = sqlite3.connect( db )       
        cursor = conn.cursor()      
        cursor.executescript( sql )   
        print "\nInitialized the database %s, based on the SQL script %s" % (db, DATABASE_SQL)
      except sqlite3.Error, e:
        print "\nFailed to initialize the database %s, based on the SQL script %s" % (db, DATABASE_SQL)
        print "Database error %s" % e.args[0]
        sys.exit(1)
      except:
        print "\nFailed to initialize the database %s, based on the SQL script %s" % (db, DATABASE_SQL)
        sys.exit(1)        
    else:
      try:
        if os.path.isfile( db ):
          conn = sqlite3.connect( db )       
          cursor = conn.cursor()
          cursor.execute("SELECT hostname FROM hosts LIMIT 1")

        try:
          if cursor:
            # error raised when getting cursor?
            print ""
        except:
          printNodb()
          sys.exit(1)
          
        if args.action == "import":
          '''
          IMPORT of an NMAP file
          '''          
          nmap_xml = DEFAULT_NMAP_XML
          if args.nmap_xml is not None:
            nmap_xml = args.nmap_xml

          parseNmapXml( nmap_xml )
          printStats( "last" )
          
        elif args.action == "stats":
          '''
          STATS of the database
          '''
          printStats()

        elif args.action == "empty":
          '''
          EMPTY the database
          '''
          if emptyDb():
            print "\nEmpty database : OK"
          else:
            print "\nEmpty database : FAIL"

        elif args.action == "clean":
          '''
          CLEAN older sessions in the database
          '''          
          cleanups = DEFAULT_CLEANUPS
          if args.cleanups is not None:
            cleanups = args.cleanups
          runCleanup( cleanups )
          
        elif args.action == "scan":
          '''
          Scan
          '''
          print "\nLaunch a scan (you will need 'root' or 'sudo' privileges)"

          output_file = DEFAULT_NMAP
          if args.output_file is not None:
            output_file = args.output_file
          ports = ""
          scripts = ""
          if args.scan_dns == True:
            scripts = " --script 'dns-recursion' "
            ports = "53"
            print " - dns-recursion"
          if args.scan_snmp == True:
            scripts = scripts + " --script 'snmp-sysdescr' "
            if ports:
              ports = ports + ","
            ports = ports + "161"
            print " - snmp-sysdescr"
          if args.scan_ntp == True:
            scripts = scripts + " --script 'ntp-info' "
            if ports:
              ports = ports + ","
            ports = ports + "123"
            print " - ntp-info"                  
          if args.scan_http == True:
            scripts = scripts + " --script 'http-title' "
            if ports:
              ports = ports + ","            
            ports = ports + "80"  
            print " - http-title"
          if args.scan_http_headers == True:
            scripts = scripts + " --script 'http-headers' --script-args http.useragent='" + HTTP_USER_AGENT + "'"
            if ports:
              ports = ports + ","            
            ports = ports + "80"  
            print " - http-headers"            
          if args.scan_dns_zone == True:
            scripts = scripts + " --script 'dns-zone-transfer' "
            if ports:
              ports = ports + ","            
            ports = ports + "53"
            print " - dns-zone-transfer"

          if ports != "": 
            if args.scan_target_input_file is not None:
              tmptarget = readTargetfile( args.scan_target_input_file )
              if tmptarget is not None:
                target = tmptarget
              else:
                target = args.scan_target
            else:
              target = args.scan_target
            print " towards : ", target
            startScan(output_file, ports, scripts, target)
            print "\nScan finished and results written to %s.xml (not yet imported). Import the data with 'import'" % output_file
          else:
            print " No ports to scan"
          
        elif args.action == "report":
          '''
          Build a report
          '''
          if args.sessions == True:
            '''
            REPORT, return the number of sessions
            '''
            print "\nNumber of sessions in database : %s " % str(countSessions())
          elif args.sessions_list == True:
            '''
            REPORT, list the sessions
            '''
            print "\nList the sessions"
            listSessions()
          elif args.sessions_list_detail == True:
            '''
            REPORT, list the sessions, detailed
            '''
            print "\nList the sessions (detailed view)"
            listSessions( "detail" )
          elif args.sessions_dump == True:
            '''
            REPORT, list the sessions, dump
            '''
            print "\nList the sessions (dump view)"            
            listSessions( "dump" )
          elif args.sessions_detail is None or  args.sessions_detail > 0:
            '''
            REPORT, list details of one session
            '''
            session_detail = args.sessions_detail
            print "\nList details of session %s" % session_detail
            dumpSession( session_detail )
          else:
            '''
            REPORT
            '''
            if args.report_session is not None:
              session = args.report_session
            else:
              session = maxSession()

            if args.report_quick == True:
              report_history = False
              report_quick = True
            else:
              report_quick = False
              if args.report_history == True:
                report_history = True
              else:
                report_history = False

            if args.report_all == True:
              service_name = "%"
              portid = 0
              protocol = "%"
              script_id = "%"
              script_output = "%"
            elif args.report_dns_zone == True:
              service_name = "domain"
              portid = 53
              protocol = "tcp"
              script_id = "dns-zone-transfer"
              script_output = "%"
            elif args.report_ntp == True:
              service_name = "ntp"
              portid = 123
              protocol = "udp"
              script_id = "ntp-info"
              script_output = "%"
            elif args.report_http == True:
              service_name = "http"
              portid = 80
              protocol = "tcp"
              script_id = "%"
              script_output = "%"                            
            elif args.report_snmp_header == True:
              service_name = "snmp"
              portid = 161
              protocol = "udp"
              script_id = "snmp-sysdescr"
              script_output = "%"
            elif args.report_dns == True:
              service_name = "domain"
              portid = 53
              protocol = "udp"
              script_id = "dns-recursion"
              script_output = "Recursion appears to be enabled"

            if portid > 0 or service_name == "%":
              buildReport( report_history, report_quick, args.report_csv, service_name, portid, protocol, script_id, script_output, session)
            else:
              print "No report type given"
    
      except:
        print "Unable to access the database %s" % db
        print "\n",sys.exc_info()
        sys.exit(1)


          
'''
 Comment
'''
'''
 Launch a scan
'''
def startScan(output_file, ports, scripts, target):
  print " ", NMAP_LOCATION, DEFAULT_SCAN_WITHOUT_PING, " -sU -sS -sV -oA ",output_file , " -p ", ports , " " , scripts , " " , target
  print getstatusoutput(NMAP_LOCATION + DEFAULT_SCAN_WITHOUT_PING + " -sU -sS -sV -oA " + output_file + " -p " + ports + " " + scripts + " " + target)


  
'''
 Dump the details of a session
'''
def dumpSession( session_detail ):
  if session_detail > 0:
    rows_script = None
    cursor.execute("SELECT hosts.ip, hosts.hostname, ports.portid, ports.protocol, ports.state, ports.script_id, ports.script_output, hosts.starttime, ports.service_name, ports.service_product, ports.service_version FROM hosts, ports WHERE hosts.ip = ports.ip AND ports.session = ?",  [session_detail])
    rows_script = cursor.fetchall()
    for row_script in rows_script:
      int_starttime = int( row_script[7] )
      str_starttime = datetime.datetime.fromtimestamp(int_starttime).strftime('%Y-%m-%d %H:%M:%S') 
      
      hostname = row_script[0]
      if hostname is None:
        hostname = "-" 
      print "%s \t %s \t %s \t%s/%s (%s %s %s %s) \n\t\t%s\t%s" % (str_starttime, hostname, row_script[1], row_script[3], row_script[2], row_script[4], row_script[8], row_script[9], row_script[10], row_script[5], row_script[6])
  else:
    print "No data found"



'''
 Get database statistics
'''
def printStats( stat_type = "all" ):
  if stat_type == "last":
    print "\nStatistics for the last session :"
    extra_sql = " WHERE session = " + str(maxSession())
  else:
    print "\nGlobal statistics :"    
    extra_sql = ""    
    
  try:
    cursor.execute("SELECT COUNT(*) AS qt FROM hosts" + extra_sql)
    row = cursor.fetchone()
    if row is not None:
      print " Records in hosts table : %s" % int(row[0])
 
    cursor.execute("SELECT COUNT(*) AS qt FROM ports" + extra_sql)
    row = cursor.fetchone()
    if row is not None:
      print " Records in ports table : %s" % int(row[0])
      
    cursor.execute("SELECT COUNT(DISTINCT ip) AS qt FROM hosts" + extra_sql)
    row = cursor.fetchone()
    if row is not None:
      print " Unique IPs : %s" % int(row[0])

    print " Maximum session ID : %s" % (maxSession())
    
  except sqlite3.Error, e:
    print "Error while generating the statistics : %s:" % e.args[0]
    sys.exit(1)



'''
 Insert a record found in the read file for httpheader
'''
def insertRecordHeader( session, ip, hostname, protocol, portid, header, data):

  header = header.strip()
  data = data.strip()
    
  if data != "HEAD)" and data != "GET)":
    try:
      cursor.execute("SELECT data FROM httpheader WHERE ip = ? AND session = ? AND protocol = ? AND portid = ? AND header = ?", (ip, session, protocol, portid, header))      
      row = cursor.fetchone()
      if row is not None:
        cursor.execute("UPDATE httpheader SET data = ? WHERE ip = ? AND session = ? AND protocol = ? AND portid = ? AND header = ?", (data, ip, session, protocol, portid, header))
      else:
        cursor.execute("INSERT INTO httpheader (ip, session, protocol, portid, header, data) VALUES ( ?, ?, ?, ? , ? , ?)", (ip, session, protocol, portid, header, data))
    except sqlite3.Error, e:
      print "Error for table httpheader %s:" % e.args[0]
      print session, ip, hostname, protocol, portid, header, data
      sys.exit(1)
    except:
      print "\nUnknown exception during insert into table httpheader", ip, portid, protocol, session 
    conn.commit()



'''
 Insert a record found in the read file
'''
def insertRecord( session, ip, hostname, hostprotocol, starttime, endtime, portid, protocol, state, service_name, service_product, service_version, service_extra, script_id, script_output):

  # Insert new host or update host
  try:
    cursor.execute("SELECT hostname FROM hosts WHERE ip = ? AND session = ?", (ip, session))
    row = cursor.fetchone()
    if row is not None: 
      if hostname:
        cursor.execute("UPDATE hosts SET hostname = ? WHERE ip = ? AND session = ?", (hostname, ip, session))
    else:
      cursor.execute("INSERT INTO hosts (ip, session, hostname, protocol, starttime, endtime) VALUES (?, ?, ?, ?, ? ,?)", (ip, session, hostname, hostprotocol, starttime, endtime)) 
  except sqlite3.Error, e:
     print "Error for table hosts  %s:" % e.args[0]
     sys.exit(1)
  except:
    print "\nUnknown exception during insert into table hosts", ip, hostprotocol, hostname, session 
  conn.commit()

  # Insert port or update port
  try: 
    cursor.execute("SELECT portid FROM ports WHERE ip = ? AND session = ? AND portid = ? AND protocol = ? ", (ip, session, portid, protocol))
    row = cursor.fetchone()
    if row is not None:
      if state:
        cursor.execute("UPDATE ports SET state = ? WHERE ip = ? AND session = ? AND protocol = ? AND portid = ?", (state,ip, session, protocol, portid))
      if script_id:
       cursor.execute("UPDATE ports SET script_id = ? WHERE ip = ? AND session = ? AND protocol = ? AND portid = ?", (script_id,ip, session, protocol, portid))
      if script_output:        
       cursor.execute("UPDATE ports SET script_output = ? WHERE ip = ? AND session = ? AND protocol = ? AND portid = ?", (script_output,ip, session, protocol, portid)) 
      if service_product:
        cursor.execute("UPDATE ports SET service_product = ? WHERE ip = ? AND session = ? AND protocol = ? AND portid = ?", (service_product,ip
, session, protocol, portid))
      if service_version:
        cursor.execute("UPDATE ports SET service_version = ? WHERE ip = ? AND session = ? AND protocol = ? AND portid = ?", (service_version,ip
, session, protocol, portid))
      if service_extra:
        cursor.execute("UPDATE ports SET service_extra = ? WHERE ip = ? AND session = ? AND protocol = ? AND portid = ?", (service_extra,ip, session, protocol, portid))
      if service_version:
        cursor.execute("UPDATE ports SET service_version = ? WHERE ip = ? AND session = ? AND protocol = ? AND portid = ?", (service_version,ip
, session, protocol, portid))

    else:
      cursor.execute("INSERT INTO ports (ip, portid, protocol, script_id, script_output, service_extra, service_name, service_product, service_version, state, session) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (ip, portid, protocol, script_id, script_output, service_extra, service_name, service_product, service_version, state, session)) 
  except sqlite3.Error, e:
     print "Error for table ports %s:" % e.args[0]
     sys.exit(1)
  except:
    print "\nUnknown exception during insert into table ports", ip, portid, protocol, session 
  conn.commit()



'''
 Parse the NMAP XML file into different variables
'''
def parseNmapXml( nmapfile ):
  print "\nImport : processing XML file %s" % nmapfile
  
  try:
    doc = etree.parse( nmapfile )
    session = maxSession() + 1
  except IOError:
    print "Error: file %s doesn't exist" % (nmapfile)
    return False
  except xml.parsers.expat.ExpatError:
    print "Error: file %s doesn't seem to be XML" % (nmapfile)
    return False
  except:
    print "Error while processing %s" % (nmapfile)

  for host in doc.getiterator("host"):
    try:
      status = host.find("status")
      
      if status is not None:
        state = status.get("state") 
        
        if (state == "up"):
          ports = host.find("ports")
          
          if ports is not None:
            address = host.find("address")
            hname = host.find("hostnames/hostname")

            ip = address.get("addr")
            hostprotocol = address.get("addrtype")
            starttime = host.get("starttime")
            endtime = host.get("endtime")
            
            if hname is not None:
              hostname = hname.get("name")
            else:
              hostname = ip

            for port in ports.getchildren():
                state_el = port.find("state")   

                if state_el is not None:
                  state = state_el.get("state")

                  if (state == "open"):
                    protocol = port.get("protocol")
                    portid = port.get("portid")

                    service = port.find("service")
                    script = port.find("script")

                    if service is not None:
                      service_name = service.get("name")
                      service_product = service.get("product")
                      service_version = service.get("version")
                      service_extra = service.get("extrainfo")
                    else:
                      service_name = ""
                      service_product = ""
                      service_version = ""
                      service_extra = ""

                    if script is not None:  
                      script_id = script.get("id")
                      script_output = script.get("output")
                    else:
                      script_id = ""
                      script_output = ""
                    
                    sys.stdout.write('+')
                    #print " Insert %s - %s (%s/%s)" % (ip, hostname, protocol, portid)
                    insertRecord( session, ip, hostname, hostprotocol, starttime, endtime, portid, protocol, state, service_name, service_product, service_version, service_extra, script_id, script_output)

                    if (script_id == "http-headers"):
                      for line in script_output.splitlines():
                        if not line:continue
                        header = line.split(":", 1)
                        if len(header) == 2:
                          insertRecordHeader( session, ip, hostname, protocol, portid, header[0], header[1])
                  else:
                    sys.stdout.write('.')   # Port state not open
                else:
                  sys.stdout.write('.')   # No port state found
          else:
            sys.stdout.write('.') # No ports found
        else:
          sys.stdout.write('.') # Host not up
      else:
        sys.stdout.write('.') # No host state found
      sys.stdout.flush()
    except Exception as e:
        print e
    except:
      print "Unable to parse the XML file %s " % nmapfile
  print "Finished processing XML file %s" % nmapfile

  

''' 
 Empty the whole database but keep the structure intact
'''
def emptyDb():
  try:
    cursor.execute("DELETE FROM hosts")
    conn.commit()
    return True
  except sqlite3.Error, e:
    print "Error %s:" % e.args[0]
    sys.exit(1)
  return False



'''
 Count the available sessions
'''
def countSessions():
  try:
    cursor.execute("SELECT COUNT(DISTINCT session) AS qt FROM hosts")
    row = cursor.fetchone()
    if row is not None:
      return int(row[0])
    else:
      return 0
  except sqlite3.Error, e:
    print "Error while counting sessions : %s:" % e.args[0]
    sys.exit(1)



'''
 List all the sessions, with first timestamp
'''
def listSessions( type = 'basic' ):
  if type != 'basic' and type != "detail" and type != "dump":
    type = "basic"
      
  try:
    cursor.execute("SELECT DISTINCT(session), starttime FROM hosts ORDER BY starttime ASC")
    rows = cursor.fetchall()
    for row in rows:
      int_starttime = int( row[1] )
      str_starttime = datetime.datetime.fromtimestamp(int_starttime).strftime('%Y-%m-%d %H:%M:%S') 
      print " Session %s : %s" % (row[0], str_starttime)
      if type == "detail":
        cursor.execute("SELECT DISTINCT(script_id) AS s, count(*) AS qt FROM ports WHERE session = ? GROUP BY script_id ORDER BY qt DESC", [row[0]])
        rows_script = cursor.fetchall()
        for row_script in rows_script:
          script_id = row_script[0]
          if script_id == "":
            script_id = "<no script provided>"
          print "   %sx %s " % (row_script[1], script_id)
      elif type == "dump":
        cursor.execute("SELECT hosts.ip, hosts.hostname, ports.portid, ports.protocol, ports.state, ports.script_id, ports.script_output FROM hosts, ports WHERE hosts.ip = ports.ip AND ports.session = ?",  [row[0]])
        rows_script = cursor.fetchall()
        for row_script in rows_script:
          hostname = row_script[0]
          if hostname is None:
            hostname = "-" 
          print "   %s - %s " % (hostname, row_script[1])          
         
  except sqlite3.Error, e:
    print "Error while listing sessions : %s:" % e.args[0]
    sys.exit(1)



'''
 Delete older data sets
'''
def runCleanup( keepruns):
  print "\nClean sessions : remove sessions older than %s runs." % keepruns
  if keepruns > 0:
   cur = countSessions()
   if cur >= keepruns:
     toclean = keepruns - cur + 1
     try:
       cursor.execute("SELECT DISTINCT session FROM hosts ORDER BY session ASC LIMIT %d" % toclean)
       rows = cursor.fetchall()
       if rows is not None:
         for row in rows:
           session = row[0]
           cursor.execute("DELETE FROM ports WHERE session = ?", [session])
           conn.commit()
           cursor.execute("DELETE FROM hosts WHERE session = ?", [session])
           conn.commit()
       print "Clean sessions : OK"
       print "  Older sessions (<= %s) removed." % keepruns
       return True
     except sqlite3.Error, e:
       print "Error %s:" % e.args[0]
       sys.exit(1)
   else:
     print "Clean sessions : FAIL"
     print "  No sessions to remove."
     return False
  else:
   emptyDb()
   return False
   


'''
 Return the maximum session ID
'''
def maxSession():
  try:
    cursor.execute("SELECT MAX(session) as mx FROM hosts")
    row = cursor.fetchone()
    if row is not None:
      mx = row[0]
      if mx is not None:
        mx = int(mx)
      else:
        mx = 0
      return mx
    else:
      return 0
  except sqlite3.Error, e:
    print "Database error %s " % e.args[0]
    sys.exit(1)   



'''
 Build a report
'''
def buildReport( history, report_quick, report_csv, service_name, portid, protocol, script_id, script_output, session):
  if portid == 0 and service_name == "%":
    print "\nReport generation for all ports and protocols"
    print " Session : %s" % session
    print " All scripts"
  else:
    print "\nReport generation for : %s %s/%s " % (service_name, portid, protocol)
    print " Session : %s" % session
    print " Script %s , verifying for output %s" % (script_id, script_output)
  try:
    if portid == 0 and service_name == "%":
      cursor.execute("SELECT hosts.ip, hosts.hostname, ports.script_output, ports.service_product, ports.service_version, hosts.starttime, hosts.endtime,ports.portid, ports.protocol, ports.script_id FROM hosts, ports WHERE hosts.ip = ports.ip AND hosts.session = ports.session AND hosts.session = ? GROUP BY hosts.ip, ports.portid,ports.protocol ORDER BY hosts.hostname ASC, hosts.ip", [session]) 
    else:
      cursor.execute("SELECT hosts.ip, hosts.hostname, ports.script_output, ports.service_product, ports.service_version, hosts.starttime, hosts.endtime,ports.portid, ports.protocol, ports.script_id FROM hosts, ports WHERE hosts.ip = ports.ip AND hosts.session = ports.session AND hosts.session = ? AND ports.portid = ? AND ports.protocol = ? AND ports.script_id LIKE ? AND ports.script_output LIKE ? ORDER BY hosts.hostname ASC, hosts.ip", ( session, portid, protocol, script_id, script_output)) 
    activehosts = cursor.fetchall()
    if activehosts is not None and len(activehosts) > 0:
      print"\n-------------------------------------"
      for activehost in activehosts:
        service_version = ""
        service_product = ""
        if activehost[3] is not None:
          service_product =  activehost[3]
        if activehost[4] is not None:
          service_version = activehost[4]

        starttime = activehost[5]
        int_starttime = int( starttime )
        str_starttime = datetime.datetime.fromtimestamp(int_starttime).strftime('%Y-%m-%d %H:%M:%S') 

        if report_quick == True:
          if report_csv == True:
            print "%s,%s,%s,%s" % (str_starttime, activehost[0],activehost[7],activehost[8])
          else:
            print "%s \t%s\t(%s/%s)" % (str_starttime, activehost[0],activehost[7],activehost[8])
        else:
          if report_csv == True:
            print "%s,%s,%s,%s,%s,%s,%s,%s" % (str_starttime, activehost[0], activehost[1], activehost[7], activehost[8], activehost[2],service_product, service_version)
          else:
            print " %s %s (%s) %s/%s \t %s \t %s \t %s" % (str_starttime, activehost[0], activehost[1], activehost[7], activehost[8], activehost[2],service_product, service_version)

        if history:
          if portid == 0 and service_name == "%":
            cursor.execute("SELECT hosts.ip, hosts.hostname, ports.script_output, hosts.starttime,ports.service_product, ports.service_version FROM hosts, ports WHERE hosts.ip = ports.ip AND hosts.session = ports.session AND hosts.starttime != ? AND hosts.ip = ? AND ports.portid = ? AND ports.protocol = ? AND hosts.session != ? GROUP BY hosts.starttime ORDER BY hosts.starttime DESC, hosts.hostname ASC, hosts.ip", ( int_starttime, activehost[0], activehost[7], activehost[8], session))
          else:
            cursor.execute("SELECT hosts.ip, hosts.hostname, ports.script_output, hosts.starttime,ports.service_product, ports.service_version FROM hosts, ports WHERE hosts.ip = ports.ip AND hosts.session = ports.session AND hosts.starttime != ? AND hosts.ip = ? AND ports.portid = ? AND ports.protocol = ? AND ports.script_id = ? AND ports.script_output = ?  AND hosts.session != ? GROUP BY hosts.starttime ORDER BY hosts.starttime DESC, hosts.hostname ASC, hosts.ip", ( int_starttime, activehost[0], portid, protocol, script_id, script_output, session)) 
          historyhosts = cursor.fetchall()
          if historyhosts is not None:
            for historyhost in historyhosts:
              int_history = int( historyhost[3] )
              str_history = datetime.datetime.fromtimestamp(int_history).strftime('%Y-%m-%d %H:%M:%S')
              service_version = ""
              service_product = ""
              if historyhost[4] is not None:
               service_product =  activehost[3]
              if historyhost[5] is not None:
               service_version = activehost[4]
              if report_csv == True:
                print "-----,%s,%s,%s,%s,%s,%s,%s" % (str_history, historyhost[0], historyhost[1], activehost[7], activehost[8], service_product, service_version) 
              else:
                print "   \_ Also on %s - %s (%s) %s/%s \t %s \t %s" % (str_history, historyhost[0], historyhost[1], activehost[7], activehost[8], service_product, service_version) 
    else:
      print "No hosts match the search"
      
  except sqlite3.Error, e:
    print "Error %s:" % e.args[0]
    sys.exit(1)



'''
 Read the target file list
'''
def readTargetfile( targetlist ):
  try:
    file = open( targetlist, 'r')
    lines = file.readlines()
  except:
    print "Unable to read %s " % targetlist
    sys.exit(1)

  return "-iL " + targetlist

'''
 Print the no database error
'''
def printNodb():
  print "\nCould not access the database. Init the database with ./noss.py init"  



'''
 Print the output header
'''
def printHeader():
  print "\n************************************"  
  print " ",APP_NAME, APP_VERSION
  print "************************************"



'''
 Jump to the main function
'''
if __name__ == "__main__":
  main()

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
#   koen dot vanimpe at cudeso dot be
#   license New BSD : http://www.vanimpe.eu/license
#
#
# 1. First run with "-i" to init the database
# 2. Then run with "-n" to parse the XML file
# 3. Use -r to regenerate the report
#


import sys
import os
import getopt
import xml.dom.minidom
import datetime, time
import sqlite3
import argparse

DATABASE = "noss.db"
DATABASE_SQL = "noss.sql"
APP_NAME = "NMAP Open Service Scan"
APP_VERSION = "0.1"


'''
 Main function, parse the app arguments
'''
def main():
  parser = argparse.ArgumentParser(description='Scan and report the open resolvers (or any other network service) in your network.', epilog='Koen Van Impe - koen dot vanimpe at cudeso dot be', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-n', '--nmap-xml', help="Process data from this NMAP input file (in XML format)")
  parser.add_argument('-r', '--report', help="Generate the report", action="store_true", default=False)
  parser.add_argument('-rh', '--history', help="Include the history in a report", action="store_true", default=False)  
  parser.add_argument('-d', '--database' , help="Database to use", default= DATABASE )
  parser.add_argument('-c', '--clean', help="Remove the older session data", default=0,const=5, type=int, nargs="?")
  parser.add_argument('-i', '--init' , help="Init the database", action="store_true", default=False)
  parser.add_argument('-x', '--empty', help="Empty the database, removing all session data", action="store_true", default=False)
  parser.add_argument('-s', '--sessions', help="Return number of sessions", action="store_true", default=False)
  parser.add_argument('-l', '--list-sessions', help="List the sessions", action="store_true", default=False)  
  parser.add_argument('-g', '--get-stats', help="Return statistics on the database", action="store_true", default=False)  
  #parser.add_argument('-dns', '--dns-open-resolver', help="Check for open resolvers", action="store_true", default=True)
  args = parser.parse_args()
  
  printHeader()

  db = args.database

  global conn, cursor

  if os.path.isfile( db ):
    conn = sqlite3.connect( db )       
    cursor = conn.cursor()
  
  if args.init == True:
    '''
    Initialize the database
    '''    
    try:
      sql = open( DATABASE_SQL, "r").read() 
      conn = sqlite3.connect( db )       
      cursor = conn.cursor()      
      cursor.executescript( sql )   
      print "\nInitialize database : OK"
      print "  %s with %s " % (db, DATABASE_SQL)
    except sqlite3.Error, e:
      print "\nInitialize database : FAIL"
      print "Database error while initializing." 
    except:
      print "\nInitialize database : FAIL"      
      print "Unable to read the SQL file (%s) or initialize the database." % DATABASE_SQL
  else:
    '''
    Do not initialize, check if the provided file is a sqlite database
    '''
    try:
      cursor.execute("SELECT hostname FROM hosts LIMIT 1")
    except:
      print "\nUnable to access %s. Not a sqlite file or file does not exist?" % db
      sys.exit(1)
      
    if args.empty == True:
      '''
      Empty the database
      '''
      if emptyDb():
        print "\nEmpty database : OK"
      else:
        print "\nEmpty database : FAIL"


    # Clean the database
    if args.clean > 0:
      print "no clean"
      # runCleanup( args.clean )

    # Import XML file
    if args.nmap_xml is not None:
      print "\nProcessing XML file %s " % args.nmap_xml
      parseNmapXml( args.nmap_xml )
      print "Finished processing XML file"

    # Get database statistics
    if args.get_stats == True and args.empty == False:
      printStats()
      
    # List the different sessions
    if args.list_sessions == True and args.empty == False:
      print "\nList all the sessions"
      listSessions()
          
    # Count the number of sessions
    if args.sessions == True and args.empty == False:
      print "\nSession count : %s." % str(countSessions())
      
    # Generate a report
    if args.report == True and args.empty == False:
      service_name = "domain"
      portid = 53
      protocol = "udp"
      script_id = "dns-recursion"
      script_output = "Recursion appears to be enabled"
      buildReport( args.history, service_name, portid, protocol, script_id, script_output)
      
  conn.close()



'''
 Get database statistics
'''
def printStats():
  try:
    print "\nStatistics :"
    cursor.execute("SELECT COUNT(*) AS qt FROM hosts")
    row = cursor.fetchone()
    if row is not None:
      print " Records in hosts table : %s" % int(row[0])
 
    cursor.execute("SELECT COUNT(*) AS qt FROM ports")
    row = cursor.fetchone()
    if row is not None:
      print " Records in ports table : %s" % int(row[0])
      
    cursor.execute("SELECT COUNT(DISTINCT ip) AS qt FROM hosts")
    row = cursor.fetchone()
    if row is not None:
      print " Unique IPs : %s" % int(row[0])

    print " Maximum session ID : %s" % (maxSession())
    
  except sqlite3.Error, e:
    print "Error while generating the statistics : %s:" % e.args[0]
    sys.exit(1)

  
  
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
  try:
    doc = xml.dom.minidom.parse(nmapfile)
    session = maxSession() + 1
  except IOError:
    print "Error: file \"%s\" doesn't exist." % (nmapfile)
    return False
  except xml.parsers.expat.ExpatError:
    print "Error: file \"%s\" doesn't seem to be XML." % (nmapfile)
    return False

  for host in doc.getElementsByTagName("host"):
    try:
      address = host.getElementsByTagName("address")[0]
      ip = address.getAttribute("addr")
      hostprotocol = address.getAttribute("addrtype")
    except:
      # move to the next host since the IP is our primary key
      continue

    try:
      hname = host.getElementsByTagName("hostname")[0]
      hostname = hname.getAttribute("name")
    except:
      hostname = ""

    try:
      status = host.getElementsByTagName("status")[0]
      state = status.getAttribute("state")
    except:
      state = ""

    try:
      starttime = host.getAttribute("starttime")
      endtime = host.getAttribute("endtime")      
    except:
      starttime = ""
      endtime = ""

    # Only do something if the host is up
    if (state == "up"):
      try:
        ports = host.getElementsByTagName("ports")[0]
        ports = ports.getElementsByTagName("port")
      except:
        # No open ports; continue to the next host
        continue

      for port in ports:
        portid = port.getAttribute("portid")
        protocol = port.getAttribute("protocol")
        state_el = port.getElementsByTagName("state")[0]
        state = state_el.getAttribute("state")

        # Only process the output if the port is marked as 'open'
        if (state == "open"):
          try:
            service = port.getElementsByTagName("service")[0]
            service_name = service.getAttribute("name")
            service_product = service.getAttribute("product")
            service_version = service.getAttribute("version")
            service_extra = service.getAttribute("extrainfo")
          except:
            service = ""
            service_name = ""
            service_product = ""
            service_version = ""
            service_extra = ""

          # Process script and service output
          for i in (0, 1):
            try:
              script = port.getElementsByTagName("script")[i]
              script_id = script.getAttribute("id")
              script_output = script.getAttribute("output")
            except:
              script_id = ""
              script_output = ""

            insertRecord( session, ip, hostname, hostprotocol, starttime, endtime, portid, protocol, state, service_name, service_product, service_version, service_extra, script_id, script_output)



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
def listSessions():
  try:
    cursor.execute("SELECT DISTINCT(session), starttime FROM hosts ORDER BY starttime ASC")
    rows = cursor.fetchall()
    for row in rows:
      int_latest_tstamp = int( row[1] )
      str_latest_tstamp = datetime.datetime.fromtimestamp(int_latest_tstamp).strftime('%Y-%m-%d %H:%M:%S') 
      print " Session %s : %s" % (row[0], str_latest_tstamp)
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
    print "Error %s:" % e.args[0]
    sys.exit(1)   



'''
 Build a report
'''
def buildReport( history, service_name, portid, protocol, script_id, script_output):
  
  print "\nReport generation for : %s %s/%s " % (service_name, portid, protocol)
  print " Script %s , verifying for output %s" % (script_id, script_output)
  try:
    # Get latest session
    session = maxSession()
    cursor.execute("SELECT starttime FROM hosts WHERE session = ? ORDER BY starttime DESC LIMIT 1", [session])
    row = cursor.fetchone()
    if row is not None:
      latest_tstamp = row[0]
      int_latest_tstamp = int( latest_tstamp )
      str_latest_tstamp = datetime.datetime.fromtimestamp(int_latest_tstamp).strftime('%Y-%m-%d %H:%M:%S') 
      print "\nData for : %s " % (str_latest_tstamp)
      cursor.execute("SELECT hosts.ip, hosts.hostname, ports.script_output, ports.service_product, ports.service_version FROM hosts, ports WHERE hosts.ip = ports.ip AND hosts.session = ports.session AND hosts.session = ? AND ports.portid = ? AND ports.protocol = ? AND ports.script_id = ? AND ports.script_output = ? ORDER BY hosts.hostname ASC, hosts.ip", ( session, portid, protocol, script_id, script_output)) 
      activehosts = cursor.fetchall()
      if activehosts is not None:
        for activehost in activehosts:
          service_version = ""
          service_product = ""
          if activehost[3] is not None:
            service_product =  activehost[3]
          if activehost[4] is not None:
            service_version = activehost[4]
           
          print " %s (%s) - %s - %s %s" % (activehost[0], activehost[1], activehost[2],service_product, service_version)
          if history:
            cursor.execute("SELECT hosts.ip, hosts.hostname, ports.script_output, hosts.tstamp,ports.service_product, ports.service_version FROM hosts, ports WHERE hosts.ip = ports.ip AND hosts.tstamp = ports.tstamp AND hosts.tstamp != ? AND hosts.ip = ? AND ports.portid = ? AND ports.protocol = ? AND ports.script_id = ? AND ports.script_output = ? ORDER BY hosts.tstamp DESC, hosts.hostname ASC, hosts.ip", ( latest_tstamp, activehost[0], portid, protocol, script_id, script_output)) 
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
                print "   \_ Also on %s - %s (%s) %s %s" % (str_history, historyhost[0], historyhost[1], service_product, service_version) 
      else:
        print "\nNo active hosts found." 
  
  except sqlite3.Error, e:
    print "Error %s:" % e.args[0]
    sys.exit(1)



'''
 Print the output header
'''
def printHeader():
  print "\n************************************"  
  print APP_NAME, APP_VERSION
  print "************************************"
  

'''
 Jump to the main function
'''
if __name__ == "__main__":
  main()

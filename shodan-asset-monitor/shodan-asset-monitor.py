#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Monitor Shodan assets and send an e-mail when new items are found
Uses a sqlite database

Koen Van Impe - 20170807

'''

import sys
import shodan
import json
import sqlite3
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from time import sleep

SHODAN_API_KEY = “SHODAN_API_KEY”

MAIL_SUBJECT="New asset found in Shodan"
MAIL_FROM=“you@example.zyx“
MAIL_RCPT="you@example.zyx"
MAIL_SMTP="localhost"
SQL_LITE_DB="shodan-asset-monitor.db"

# Set this to True for debug output on screen
PRINT_PROGRESS = True

api = shodan.Shodan(SHODAN_API_KEY)
conn = sqlite3.connect(SQL_LITE_DB, timeout=10)

def notify_update(query, ip_str, asn, org, country_code, modified, port, transport, product, devicetype, timestamp):
    msg = MIMEMultipart()
    msg['Subject'] = "%s - %s - %s %s/%s" % (MAIL_SUBJECT, query, ip_str, port, transport)
    msg['From'] = MAIL_FROM
    msg['To'] = MAIL_RCPT
    body = "A new asset has been found by the Shodan monitor. \n Timestamp: %s \n IP: %s \n Port: %s / %s \n ASN: %s \n Org: %s \n Country: %s \n Product: %s \n Devicetype: %s" % (timestamp, ip_str, transport, port, asn, org, country_code, product, devicetype)
    csvcontent = "'%s','%s', '%s', '%s', '%s', '%s', '%s' , '%s', '%s'" % (timestamp, ip_str, transport, port, asn, org, country_code, product, devicetype)
    attachment = MIMEText(csvcontent)
    attachment.add_header('Content-Disposition', 'attachment', filename='shodan-asset.csv')
    msg.attach(MIMEText(body, 'plain'))
    msg.attach(attachment)

    server = smtplib.SMTP(MAIL_SMTP)
    text = msg.as_string()
    
    server.sendmail(MAIL_FROM, MAIL_RCPT, text)
    server.quit()

def do_search(query):
    results = api.search(query)
    if PRINT_PROGRESS:
        print "Results found for %s : %s" % (query, results['total'])
    
    for result in results['matches']:
        ip_str = result['ip_str']
        asn = result.get('asn', 'n/a')
        org = result.get('org', 'n/a')
        location = result["location"]
        country_code = location.get('country_code', 'n/a') 

        try:
            shodan_host = api.host( ip_str )

            for item in shodan_host['data']:

                timestamp = item['timestamp']
                port = item.get('port', 0)
                transport = item.get('transport','n/a')
                product = item.get('product', 'n/a')
                devicetype = item.get('devicetype', 'n/a')
                            
                if PRINT_PROGRESS:
                    print " Processing %s , timestamp %s port %s transport %s " % (ip_str, timestamp, port, transport)

                # Get the modified value
                cur = conn.cursor()
                cur.execute("SELECT modified FROM host_items WHERE ip_str = ? AND port = ? AND transport = ?", (ip_str, port, transport))
                row_result = cur.fetchone()

                # If no results are retrieved this means it's a new record
                if row_result is not None:
                    modified = row_result[0]
                else:
                    modified = None

                if modified is None:
                    if PRINT_PROGRESS:
                        print "New record"
                    cur.execute("INSERT INTO host_items (ip_str, asn, org, country_code, created, modified, port, transport, product, devicetype) VALUES (?, ?, ? ,?, ?, ?, ?, ?, ?, ?)", (ip_str,asn, org, country_code, timestamp, timestamp, port, transport, product, devicetype))
                    notify_update(query, ip_str, asn, org, country_code, modified, port, transport, product, devicetype, timestamp)
                else:
                    # Is the record newer than the existing timestamp
                    if modified < timestamp:
                        # Update the record with the new timestamp, it's not a new sighting
                        if PRINT_PROGRESS:
                            print "Update record"
                        cur.execute("UPDATE host_items SET modified = ? WHERE ip_str = ? AND port = ? AND transport = ?", (timestamp, ip_str, port, transport))
                    else:
                        if PRINT_PROGRESS:
                            print "Record found but no new timestamp"
                sleep(0.1)
            conn.commit()

        except shodan.APIError, e:
            print ' Error: %s' % e
            pass
        except sqlite3.Error as e:
            print ' Error: %s' % e.message            
        except:
            print " Other error", sys.exc_info()[0]
            pass


def main():
    try:
        if len(sys.argv) > 1 and sys.argv[1] is not None:
            SEARCH_QUERY = sys.argv[1]
            do_search(SEARCH_QUERY)
        else:
            print "You need to provide a search query"        
    except shodan.APIError, e:
        print 'Error: %s' % e
    
if __name__ == "__main__":
    main()

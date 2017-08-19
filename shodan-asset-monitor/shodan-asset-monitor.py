#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Monitor Shodan assets and send an e-mail when new items are found
Uses a sqlite database

Koen Van Impe - 20170818

shodan-asset-monitor.py <searchstring> [no]

<searchstring>  : string to query Shodan
[no]            : optional : 'any' argument disables email notification (ideal for first run)

'''

import sys
import shodan
import json
import sqlite3
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from time import sleep

SHODAN_API_KEY = "SHODAN_API_KEY"

MAIL_SUBJECT="Shodan Monitor"
MAIL_FROM="you@example.zyx"
MAIL_RCPT="you@example.zyx"
MAIL_SMTP="localhost"
SQL_LITE_DB="shodan-asset-monitor.db"

# Set this to True for debug output on screen
PRINT_PROGRESS = True
NOTIFY_MAIL= True

api = shodan.Shodan(SHODAN_API_KEY)
conn = sqlite3.connect(SQL_LITE_DB, timeout=10)

# Send out notification e-mail + attachment
def notify_host(query, ip_str, action, extra_body_text):

    if NOTIFY_MAIL and ip_str:
        csvcontent = "'Last modified','IP', 'Hostname', 'Transport', 'Port', 'ASN', 'Org', 'Country', 'Product', 'Device type'\n"
        cur = conn.cursor()
        cur.execute("SELECT ip_str, port, transport, modified, product, devicetype, hostname, asn, org, country_code  FROM host_items WHERE ip_str = ? ORDER BY modified DESC", [ip_str])
        row_result = cur.fetchall()
        for rec in row_result:
            #0:=ip_str     1:port   2: transport 3: timestamp  4:product  5:devicetype  6:hostname, 7:asn, 8:org  9:country
            csvcontent = csvcontent + "'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'\n" % (rec[3], rec[0], rec[6], rec[2], rec[1], rec[7], rec[8], rec[9], rec[4], rec[5])

        msg = MIMEMultipart()
        host_mailinfo = "Timestamp: %s \n IP: %s \n Hostname: %s \n ASN: %s \n Org: %s \n Country: %s" % (rec[3], ip_str, rec[6], rec[7], rec[8], rec[9])
        query = unicode(query, 'utf-8')
        if action == "new":
            msg["Subject"] = "%s - %s - New Host : %s" % (MAIL_SUBJECT, query, ip_str)
            body = "New host found by Shodan monitor: \n " + host_mailinfo
        else:
            msg["Subject"] = "%s - %s - Changed Host : %s" % (MAIL_SUBJECT, query, ip_str)
            body = "Changed host found by Shodan monitor: \n " + host_mailinfo
            body = body + extra_body_text

        msg["From"] = MAIL_FROM
        msg["To"] = MAIL_RCPT

        attachment = MIMEText(csvcontent)
        attachment.add_header("Content-Disposition", "attachment", filename="shodan-asset.csv")
        msg.attach(MIMEText(body, "plain"))
        msg.attach(attachment)

        server = smtplib.SMTP(MAIL_SMTP)
        text = msg.as_string()
        server.sendmail(MAIL_FROM, MAIL_RCPT, text)
        server.quit()


# Convert Shodan returned record to a cleaned construct
def convert_shodan_record(item):
    timestamp = item["timestamp"]
    port = item.get("port", 0)
    transport = item.get("transport","n/a")
    product = item.get("product", "n/a")
    devicetype = item.get("devicetype", "n/a")

    return {    "timestamp": timestamp,
                "port": port,
                "transport": transport,
                "product": product,
                "devicetype": devicetype
                }


# Perform the search at Shodan
def do_search(query):
    results = api.search(query)
    if PRINT_PROGRESS:
        print "Results found for %s : %s" % (query, results["total"])
    
    for result in results["matches"]:
        ip_str = result["ip_str"]
        asn = result.get("asn", "n/a")
        org = result.get("org", "n/a")
        location = result["location"]
        country_code = location.get("country_code", "n/a")
        hostname_res = result.get("hostnames", "n/a")
        if len(hostname_res) > 0:
            hostname = hostname_res[0]
        else:
            hostname = "n/a"
        if hostname is None or hostname == "":
            hostname = "n/a"

        try:
            if PRINT_PROGRESS:
                print " Processing %s" % ip_str

            # Fetch Shodan details
            shodan_host = api.host( ip_str )

            # Check if this is a new host
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM host_items WHERE ip_str = ?", [ip_str])
            row_result = cur.fetchone()
            qt = row_result[0]

            # A new host
            if qt == 0:

                # Process all ports
                for item in shodan_host["data"]:
                    shodan_data = convert_shodan_record(item)
                    if PRINT_PROGRESS:
                        print "  New record %s/%s" % (shodan_data["port"], shodan_data["transport"])

                    cur.execute("INSERT INTO host_items (ip_str, hostname, asn, org, country_code, created, modified, port, transport, product, devicetype) VALUES (?, ?, ?, ? ,?, ?, ?, ?, ?, ?, ?)", (ip_str, hostname, asn, org, country_code, shodan_data["timestamp"], shodan_data["timestamp"], shodan_data["port"], shodan_data["transport"], shodan_data["product"], shodan_data["devicetype"]))
                    conn.commit()

                # Prepare for notification mail
                notify_host(query, ip_str, "new", "")

            # Existing host
            else:
                if PRINT_PROGRESS:
                    print "  Existing host, verifying records."
                host_has_changed = False
                changed_records = ""

                # Process all ports
                for item in shodan_host["data"]:
                    shodan_data = convert_shodan_record(item)

                    # Verify Shodan with 'modified' of found record
                    cur = conn.cursor()
                    cur.execute("SELECT modified FROM host_items WHERE ip_str = ? AND port = ? AND transport = ?", (ip_str, shodan_data["port"], shodan_data["transport"]))
                    row_result = cur.fetchone()
                    
                    # If no results are retrieved this means it's a new record
                    if row_result is not None:
                        modified = row_result[0]
                    else:
                        modified = None

                    if modified is None:
                        host_has_changed = True
                        if PRINT_PROGRESS:
                            print "  New record %s/%s" % (shodan_data["port"], shodan_data["transport"])
                        changed_records = changed_records + "\n Added : %s/%s - %s - %s" % (shodan_data["port"], shodan_data["transport"], shodan_data["product"], shodan_data["devicetype"])
                        cur.execute("INSERT INTO host_items (ip_str, hostname, asn, org, country_code, created, modified, port, transport, product, devicetype) VALUES (?, ?, ?, ? ,?, ?, ?, ?, ?, ?, ?)", (ip_str, hostname, asn, org, country_code, shodan_data["timestamp"], shodan_data["timestamp"], shodan_data["port"], shodan_data["transport"], shodan_data["product"], shodan_data["devicetype"]))
                    else:
                        # Is the record newer than the existing timestamp
                        if modified < shodan_data["timestamp"]:
                            # Update the record with the new timestamp, it's not a new sighting
                            if PRINT_PROGRESS:
                                print "  Update record %s/%s" % (shodan_data["port"], shodan_data["transport"])
                            # Update string but don't mark host as changed
                            changed_records = changed_records + "\n Timestamp changed : %s/%s (%s)" % (shodan_data["port"], shodan_data["transport"], shodan_data["timestamp"])
                            cur.execute("UPDATE host_items SET modified = ? WHERE ip_str = ? AND port = ? AND transport = ?", (shodan_data["timestamp"], ip_str, shodan_data["port"], shodan_data["transport"]))
                        else:
                            if PRINT_PROGRESS:
                                print "  Record %s/%s found in Shodan but no new update" % (shodan_data["port"], shodan_data["transport"])
                    conn.commit()
                    sleep(0.1)
                
                # Any changes?
                if host_has_changed:
                    changed_records = "\n\n Changes\n-----------\n" + changed_records
                    notify_host(query, ip_str, "update", changed_records)

        
        except shodan.APIError, e:
            print ' Error: %s' % e
            pass
        except sqlite3.Error as e:
            print " Error: %s" % e.message            
        except:
            print " Other error", sys.exc_info()[0]
            
        

def main():
    global NOTIFY_MAIL

    try:
        if len(sys.argv) > 1 and sys.argv[1] is not None:
            SEARCH_QUERY = sys.argv[1]            

            # Extra argument after search : do not send notify mails
            if len(sys.argv) == 3:
                NOTIFY_MAIL = False

            do_search(SEARCH_QUERY)

        else:
            print "You need to provide a search query!"        
    except shodan.APIError, e:
        print "Error: %s" % e
    
if __name__ == "__main__":
    main()

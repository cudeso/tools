#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Monitor Shodan assets and send an e-mail when new items are found
Uses a sqlite database

Koen Van Impe - v2 - 20171112
Koen Van Impe - v1 - 20170818

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

# For http module, use the title as "product", except for these responses
exclude_http_title = [ "Document Moved","Bad Request","Home Loading Page","webserver",
                    "400 Bad Request !!!","400 Bad Request","400 The plain HTTP request was sent to HTTPS port",
                    "401 Unauthorized","Error 401 - Unauthorized","401 Authorization Required",
                    "403 - Forbidden: Access is denied.","403 Interdit","403 Verboden","403 Forbidden", "Document Error: Page not found",
                    "404 Not found","404 Not Found","404 - Not Found", 
                    "500 Internal Server Error",
                    "302 Found","301 Moved Permanently", "307 Temporary Redirect",
                    "Protected Object","Object moved","Not Found","Web managerment Home",
                    "The page is not found", "Unauthorized","Index","Object Not Found",                                        
                    "Document Error: Unauthorized","Service Unavailable","Invalid Request",
                    "You are not authorized to view this page","Not Found","Index of .","Index page",
                    "ERROR: The requested URL could not be retrieved","Moved","Nothing to see here!",
                    "Site under construction","Untitled Document","User access verification."
                    "Error response","Home Loading Page","Inloggen","Login","index","Web Client"]

# Set this to True for debug output on screen
PRINT_PROGRESS = True
NOTIFY_MAIL= True

api = shodan.Shodan(SHODAN_API_KEY)
conn = sqlite3.connect(SQL_LITE_DB, timeout=10)

# Send out notification e-mail + attachment
def notify_host(query, ip_str, action, extra_body_text):

    if NOTIFY_MAIL and ip_str:
        csvcontent = "'Last modified','IP', 'Hostname', 'Transport', 'Port', 'ASN', 'Org', 'Country', 'Product', 'Device type', 'Shodanmodule','VendorID'\n"
        cur = conn.cursor()
        cur.execute("SELECT ip_str, port, transport, modified, product, devicetype, hostname, asn, org, country_code, shodanmodule, vendorid  FROM host_items WHERE ip_str = ? ORDER BY modified DESC", [ip_str])
        row_result = cur.fetchall()
        for rec in row_result:
            #0:=ip_str     1:port   2: transport 3: timestamp  4:product  5:devicetype  6:hostname, 7:asn, 8:org  9:country  10:shodanmodule  11:vendorid
            csvcontent = csvcontent + "'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'\n" % (rec[3], rec[0], rec[6], rec[2], rec[1], rec[7], rec[8], rec[9], rec[4], rec[5], rec[10], rec[11])

        msg = MIMEMultipart()
        host_mailinfo = "Timestamp: %s \n IP: %s \n Hostname: %s \n ASN: %s \n Org: %s \n Country: %s" % (rec[3], ip_str, rec[6], rec[7], rec[8], rec[9])
        host_mailinfo = host_mailinfo + "\n Shodan URL: https://www.shodan.io/host/%s" % ip_str        
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

        attachment = MIMEText(csvcontent.encode('utf-8'))
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
    devicetype = item.get("device_type", "n/a")
    vendorid = item.get("vendor_id", "n/a")
    data = item.get("data", "")
    shodan_meta = item.get("_shodan")
    shodanmodule = shodan_meta.get("module", "n/a")


    # Can we extract info based on the module used by Shodan?
    if shodanmodule and data:
        if shodanmodule == "bacnet":
            data_s = data.split("\n")
            for el in data_s:
                if "Vendor Name" in el:                    
                    if vendorid == "n/a":
                        vendorid = el[len("Vendor Name") + 2:]
                elif "Model Name" in el:
                    if product == "n/a":
                        product = el[len("Model Name") + 2:]

        elif (shodanmodule == "http-simple-new" or shodanmodule == "http" or shodanmodule == "http-simple" or shodanmodule == "http-check"):
            product = "http"
            title = item.get("title", "n/a")
            if title != "n/a" and title not in exclude_http_title:
                product = title
                    
        elif shodanmodule == "telnet":
            data_s = data.split("\n")
            if product == "n/a":
                try:
                    product = data_s[2]
                except:
                    pass

        elif shodanmodule == "rtsp-tcp":
            data_s = data.split("\n")
            for el in data_s:
                if "Server: " in el:
                    if product == "n/a":
                        product = el[len("Server") + 2:]  

        elif shodanmodule == "s7":
            data_s = data.split("\n")
            for el in data_s:
                if "Copyright" in el:
                    if vendorid == "n/a":
                        vendorid = el[len("Copyright") + 2:]
                elif "Module type" in el:
                    if product == "n/a":
                        product = el[len("Module type") + 2:]

    # Clean up unwanted strings from product, vendor and devicetype
    product = product.strip("/\n,/\r").replace("&nbsp;", " ").strip()
    vendorid = vendorid.strip("/\n,/\r").replace("&nbsp;", " ").strip()
    devicetype = devicetype.strip("/\n,/\r").replace("&nbsp;", " ").strip()
    
    return {    "timestamp": timestamp,
                "port": port,
                "transport": transport,
                "product": product,
                "devicetype": devicetype,
                "vendorid": vendorid,
                "shodanmodule": shodanmodule,
                "data": data
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
        try:
            domains = result["domains"]
            domain = domains[0]
        except:
            domain = ""        
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
                        print "  New record %s/%s (%s via %s)" % (shodan_data["port"], shodan_data["transport"], shodan_data["product"], shodan_data["shodanmodule"])

                    cur.execute("INSERT INTO host_items (ip_str, hostname, asn, org, country_code, created, modified, port, transport, product, devicetype, shodanmodule, domain, data, searchquery, vendorid) VALUES (?, ?, ?, ? ,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (ip_str, hostname, asn, org, country_code, shodan_data["timestamp"], shodan_data["timestamp"], shodan_data["port"], shodan_data["transport"], shodan_data["product"], shodan_data["devicetype"], shodan_data["shodanmodule"], domain, shodan_data["data"], query, shodan_data["vendorid"]))
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
                            print "  New record %s/%s (%s via %s)" % (shodan_data["port"], shodan_data["transport"], shodan_data["product"], shodan_data["shodanmodule"])
                        changed_records = changed_records + "\n Added : %s/%s - %s - %s" % (shodan_data["port"], shodan_data["transport"], shodan_data["product"], shodan_data["devicetype"])
                        cur.execute("INSERT INTO host_items (ip_str, hostname, asn, org, country_code, created, modified, port, transport, product, devicetype, shodanmodule, domain, data, searchquery, vendorid) VALUES (?, ?, ?, ?, ?, ?, ?, ? ,?, ?, ?, ?, ?, ?, ?, ?)", (ip_str, hostname, asn, org, country_code, shodan_data["timestamp"], shodan_data["timestamp"], shodan_data["port"], shodan_data["transport"], shodan_data["product"], shodan_data["devicetype"], shodan_data["shodanmodule"], domain, shodan_data["data"], query, shodan_data["vendorid"]))
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

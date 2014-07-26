#!/usr/bin/python
#
# Get traffic_raw from Arbor Peakflow and check for connections
# to a list of interesting networks from a CSV file
#
# Inline configuration
#   url :   Remote URL with CSV containing the networks to check
#   dst_ip_in_csv   :   field in the CSV containing the IPs / networks
#   request_url :   URL to Arbor Peakflow (https://arbor.host.com/arborws/traffic?)
#   api_key :   api_key for Arbor Peakflow
#   timeout     :   timeout for Arbor Peakflow request
#   search_limit    :   limit results
#   mail_rcpt   :   mail receiver
#   mail_from   :   mail sender
#   mail_server : mail server to use
#
#
# Koen Van Impe
#   koen.vanimpe@cudeso.be      @cudeso         http://www.vanimpe.eu
#   20140726
#
#

import urllib,urllib2
import csv
import StringIO
import smtplib
import datetime
from email.mime.text import MIMEText
from lxml import etree

url = 'http://myhost/cc.csv'
api_key = '123'
request_url = 'https://arbor.myhost/arborws/traffic?'
mail_rcpt = "<>"
mail_from = "<>"
mail_server = "127.0.0.1"
timeout = 300
search_limit = 200
dst_ip_in_csv = 0

arbor_prepend = '<?xml version="1.0" encoding="utf-8"?><peakflow version="2.0"><query type="traffic_raw">'
arbor_prepend = arbor_prepend + '<time start_ascii="24 hours ago" end_ascii="now"/>'
arbor_prepend = arbor_prepend + '<search limit="' + str(search_limit) + '" timeout="' + str(timeout) + '" ip_ver="4"/>'
arbor_prepend = arbor_prepend + '<filter type="fcap">'
arbor_prepend = arbor_prepend + '<instance value="'
arbor_postpend = '"/></filter></query></peakflow>'
cur_date = datetime.datetime.utcnow()
counter = 0
querystring = ''

data = urllib2.urlopen( url )
csv = csv.reader( data )


for row in csv:
    if counter > 0:
        querystring = querystring + ' or '
    querystring = querystring + ' dst net ' + row[dst_ip_in_csv]
    counter = counter + 1

if len(querystring) > 0:
    xml = arbor_prepend + querystring + arbor_postpend
    encoded_xml = urllib.quote(xml)
    arbordata = urllib2.urlopen( request_url + 'api_key=' + api_key + '&query=' + encoded_xml )
    response = arbordata.read()

    output = "src_ip, src_port, dst_ip, dst_port, proto, packets, bytes"
    doc = etree.fromstring(response)
    for flow in doc.getiterator('flow'):
        src_ip = flow.get('src_ip')
        if src_ip is not None:
            dst_ip = flow.get('dst_ip')
            src_port = flow.get('src_port')
            dst_port = flow.get('dst_port')
            proto = flow.get('proto')
            packets = flow.get('packets')
            bytes = flow.get('bytes')
            output = output + "\n%s,%s,%s,%s,%s,%s,%s" % ( src_ip, src_port, dst_ip, dst_port, proto, packets, bytes)

    try:
        message = MIMEText( output )
        message["Subject"] = "Arbor Peakflow connections %s " % cur_date
        message["From"] = mail_from
        message["To"] = mail_rcpt
        smtpObj = smtplib.SMTP( mail_server )
        smtpObj.sendmail(mail_from, mail_rcpt, message.as_string())
        smtpObj.quit()
    except smtplib.SMTPException:
        print "Unable to send mail"

    
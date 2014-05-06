#!/usr/bin/python
#
# Check Expiration Date of SSL certificates
#
# Koen Van Impe
#
# Uses the file ceds.checks as input ; one entry per line, format <host>:<port>
#
#  ceds.checks :            www.google.com:443
#                           imap.mydomain.tld:993
#                       


from OpenSSL import SSL
import socket, datetime
import smtplib
from email.mime.text import MIMEText

servers_to_check = "ceds.checks"
alert_days = 5
mail_rcpt = "<>"
mail_from = "<>"
mail_server = "127.0.0.1"

servers = open( servers_to_check, "r")
cur_date = datetime.datetime.utcnow()
response = ""
cert_tested = 0

for line in servers:
    host = line.strip().split(":")[0]
    port = line.strip().split(":")[1]
    try:
        context = SSL.Context(SSL.SSLv23_METHOD)
        sock = SSL.Connection(context, socket.socket(socket.AF_INET, socket.SOCK_STREAM))

        try:
            sock.connect( (str(host) , int(port)) )
            sock.send("\x00")       # Send empty to trigger response
            get_peer_cert=sock.get_peer_certificate()
            sock.close()

            exp_date =  datetime.datetime.strptime(get_peer_cert.get_notAfter(),'%Y%m%d%H%M%SZ')        
            days_to_expire = int((exp_date - cur_date).days)
            cert_tested = cert_tested + 1

            if days_to_expire < 0:
                response = response + "\n %s : %s EXPIRED" % (host, port)
            elif alert_days > days_to_expire:
                response = response + "\n %s : %s expires in %s dayes " % (host, port, days_to_expire)
            #else:
                #response = response + "\n %s : %s OK" % (host,port)
        except:
            response = response + "\n Unable to connect to %s : %s " % (host, port)
    except SSL.Error,e:
        print e

if response:
    response = response + "\n\nTotal certificates tested : %s \n" % cert_tested
    try:
        message = MIMEText( response )
        message["Subject"] = "Certificate check %s " % cur_date
        message["From"] = mail_from
        message["To"] = mail_rcpt
        smtpObj = smtplib.SMTP( mail_server )
        smtpObj.sendmail(mail_from, mail_rcpt, message.as_string())
        smtpObj.quit()
    except smtplib.SMTPException:
        print "Unable to send mail"

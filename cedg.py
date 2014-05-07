#!/usr/bin/python
#
# Check Expiration Date of GPG keys
#
# Koen Van Impe
#
# Uses the file cedg.checks as input ; one entry per line, format <keyid>
#
# Configure inline
#
#   keys_to_check = "cedg.checks"           File with the keys
#   alert_days = 5                          Send alert when close to x days
#   mail_rcpt = ""                          Recpt of alert
#   mail_from = ""                          Sender of alert
#   mail_server = "localhost"               Mailserver to use
#   key_server = "keyserver.ubuntu.com"     Keyserver to use
#   gpg_location = "/home/gpgtest/.gnupg"   Location of GPG ring
#   delete_keys = True                      Delete the keys before launch   (True/False)
#   import_keys = True                      Import the keys from keyserver  (True/False)
#   simple_output = False                   Extended or simple layout       (True/False)

import gnupg
import datetime
import smtplib
from email.mime.text import MIMEText

keys_to_check = "cedg.checks"
alert_days = 5
mail_rcpt = "<>"
mail_from = "<>"
mail_server = "127.0.0.1"
key_server = "keyserver.ubuntu.com"
gpg_location = "/home/gpgtest/.gnupg"
delete_keys = True
import_keys = True
simple_output = False

cur_date = datetime.datetime.utcnow()
keyset = open( keys_to_check, "r")
gpg = gnupg.GPG(gnupghome=gpg_location)
response = ""
simple_response = ""

# Delete the existing keys or not?
if delete_keys:
    response = response + "Start with deleting keys\n"
    public_keys = gpg.list_keys()
    for key in public_keys:
        fingerprint = key["fingerprint"]
        uid = key["uids"]
        keyid = key["keyid"]
        result = gpg.delete_keys( fingerprint )
        if str(result) == "ok":
            response = response +  " Delete key ( %s ) %s \n" % (keyid, uid)
        else:
            response = response + " Delete key ( %s ) %s FAILED \n" % (keyid, uid)
    response = response + "Key deletion finished\n"


# Import the keys from a keyserver
if import_keys:
    response = response + "\nImporting keys\n"
    for line in keyset:
        key = line.strip()
        response = response + "Process key %s : " % key
        try:
            result = gpg.recv_keys( key_server, key )
            if result:
                response = response + " Imported\n"
            else:
                response = response + "  Unable to download key from %s \n" % key_server 
        except:
            response = response + "  Unable to download key from %s \n" % key_server 


# Verify if any of the keys have expired
response = response + "\nParsing keys\n"
public_keys = gpg.list_keys()
for key in public_keys:
    expires = key["expires"]
    uid = key["uids"]
    keyid = key["keyid"]    
    if expires:
        fl_expires = datetime.datetime.fromtimestamp( float(expires) )
        str_expire = datetime.datetime.fromtimestamp( float(expires) ).strftime('%Y-%m-%d %H:%M:%S')
        days_to_expire = int((fl_expires - cur_date).days)
        if days_to_expire < 0:
            response = response + " ** Key ( %s ) %s has EXPIRED (%s) **\n" % (keyid, uid, str_expire)
            simple_response = simple_response + " ** Key ( %s ) %s has EXPIRED (%s) **\n" % (keyid, uid, str_expire)
        elif alert_days > days_to_expire:
            response = response + " ** Key ( %s ) %s expires in %s days (%s) **\n" % (keyid, uid, days_to_expire, str_expire)
            simple_response = simple_response + " ** Key ( %s ) %s expires in %s days (%s) **\n" % (keyid, uid, days_to_expire, str_expire)
        else:
            response = response + " Key ( %s ) %s expires in %s days (%s) \n" % (keyid, uid, days_to_expire, str_expire)
    else:
        response = response + " No expiration date ( %s ) %s \n" % (keyid, uid)
    
# Report
if simple_output:
    response = simple_response

# Send the report
try:
    message = MIMEText( response )
    message["Subject"] = "GPG Expiration check %s " % cur_date
    message["From"] = mail_from
    message["To"] = mail_rcpt
    smtpObj = smtplib.SMTP( mail_server )
    smtpObj.sendmail(mail_from, mail_rcpt, message.as_string())
    smtpObj.quit()
except smtplib.SMTPException:
    print "Unable to send mail"

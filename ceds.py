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


import socket
import datetime
import ssl
import smtplib
from email.message import EmailMessage
try:
    from cryptography.x509 import load_der_x509_certificate

    def fallbackGetExpire(host, port):
        try:
            with socket.create_connection((host, port)) as s:
                with context_no_verify.wrap_socket(s) as sock:
                    sock.do_handshake()
                    cert = sock.getpeercert(True)
                    sock.close()
            return load_der_x509_certificate(cert).not_valid_after
        except Exception as e:
            print("Error while falling back", e)
            return None
except ImportError:
    def fallbackGetExpire(host, port):
        return None

servers_to_check = "ceds.checks"
alert_days = 5
mail_rcpt = "<>"
mail_from = "<>"
mail_server = "127.0.0.1"
socket.setdefaulttimeout(300)

servers = open(servers_to_check, "r")
cur_date = datetime.datetime.utcnow()
response = ""
cert_tested = 0
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context_no_verify = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context_no_verify.check_hostname = False
context_no_verify.verify_mode = ssl.CERT_NONE

for line in servers:
    if not line.strip():
        continue
    host, port = line.strip().rsplit(":", 1)
    try:
        exp_date = None
        try:
            with socket.create_connection((host, port)) as s:
                with context.wrap_socket(s, server_hostname=host) as sock:
                    sock.do_handshake()
                    cert = sock.getpeercert()
                    sock.close()

            exp_date = datetime.datetime.fromtimestamp(
                ssl.cert_time_to_seconds(cert['notAfter'])
            )
        except ssl.SSLCertVerificationError:
            exp_date = fallbackGetExpire(host, port)
            response = response + "\n %s : %s hostname mismatch" % (
                host, port
            )
        except Exception as exc:
            response = response + "\n Unable to connect to %s : %s " % (
                host, port
            )
            print(exc)
        cert_tested = cert_tested + 1
        if not exp_date:
            continue
        days_to_expire = int((exp_date - cur_date).days)

        if days_to_expire < 0:
            response = response + "\n %s : %s EXPIRED" % (host, port)
        elif alert_days > days_to_expire:
            response = response + \
                "\n %s : %s expires in %s dayes " % (
                    host, port, days_to_expire)
        # else:
            # response = response + "\n %s : %s OK" % (host,port)
    except Exception as e:
        print(cert)
        print(e)

if response:
    response = response + "\n\nTotal certificates tested : %s \n" % cert_tested
    try:
        message = EmailMessage()
        message["Subject"] = "Certificate check %s " % cur_date
        message["From"] = mail_from
        message["To"] = mail_rcpt
        message.set_content(response)
        with smtplib.SMTP(mail_server) as smtpObj:
            smtpObj.send_message(message)
    except (smtplib.SMTPException, ConnectionRefusedError):
        print("Unable to send mail, response :")
        print(response)

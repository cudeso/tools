#!/usr/bin/env python
#
# Get mails from IMAP folder and store in sqlite
#
# Koen Van Impe
#
# Koen Van Impe
#   koen.vanimpe@cudeso.be      @cudeso         http://www.vanimpe.eu
#   20150502
#           


import imaplib
import email
import sys
import sqlite3
import hashlib
EMPTY_DATABASE=True
DATABASE="mail-header.db"

MAIL_SERVER="127.0.0.1"
MAIL_FOLDER="inbox"
MAIL_SSL=False
MAIL_USERNAME="myuser"
MAIL_PASSWORD="mypassword"


def main():
    global conn, cursor

    try:
        conn = sqlite3.connect( DATABASE )       
        cursor = conn.cursor()

        if EMPTY_DATABASE:
            emptyDb()

        mailid = 0
        try:
            if MAIL_SSL:
                mail = imaplib.IMAP4_SSL( MAIL_SERVER )
            else:
                mail = imaplib.IMAP4( MAIL_SERVER )
            mail.login( MAIL_USERNAME , MAIL_PASSWORD )
            mail.select( MAIL_FOLDER )
            # Get the list of available folders
            print mail.list()
            #mail.select("inbox")

            typ, data = mail.search(None, 'ALL')
            for mailid in data[0].split():
                #if int(mailid) > 9:
                #    break
                typ, data = mail.fetch(mailid, '(RFC822)')
                raw_email = data[0][1]
                email_message = email.message_from_string(raw_email)
                multi_part = email_message.is_multipart()
                number_of_headers = email_message.__len__()
                
                content_type = email_message.get_content_type()
                full_length_message = len(email_message.as_string())
                md5 = hashlib.md5(email_message.as_string()).hexdigest()
                subject = email_message["subject"]
                subject_len = len(subject)
                subject_md5 = hashlib.md5(subject).hexdigest()
                subject_stripped_md5 = hashlib.md5(subject.strip().lower()).hexdigest()
                                
                headers = email_message.items()
                print "Processed E-mail %s " % mailid
                try:
                    cursor.execute('INSERT INTO mails (mailid, content_type, full_length, md5, multi_part, number_headers, subject, subject_len, subject_md5, subject_stripped_md5) VALUES (?, ? , ?, ?, ?, ?, ?, ?, ?, ?)', (mailid, content_type, full_length_message, md5, multi_part, number_of_headers, subject, subject_len, subject_md5, subject_stripped_md5))
                    for header in headers:
                        header_stripped = header[0].encode('utf8').strip().lower()
                        value_stripped = header[1].encode('utf8').strip().lower()                        
                        cursor.execute('INSERT INTO headers (mailid, header, value, header_stripped, value_stripped) VALUES (?, ?, ?, ?, ?)', (mailid, header[0].encode('utf8'), header[1].encode('utf8'), header_stripped, value_stripped))
                    conn.commit()
                except Exception, e:
                      print e
                      continue                    
        except sqlite3.Error, e:
             print "SQL error %s:" % e.args[0]
             sys.exit(1)
        except:
            print "Unexpected error:", sys.exc_info()[0]

        print "Mails processed : %s" % mailid

    except sqlite3.Error, e:
        print "Database error %s" % e.args[0]
        sys.exit(1)

    sys.exit(1)

def emptyDb():
  try:
    cursor.execute("DELETE FROM headers")
    cursor.execute("DELETE FROM mails")
    conn.commit()
    return True
  except sqlite3.Error, e:
    print "Error %s:" % e.args[0]
    sys.exit(1)
  return False
  
if __name__ == "__main__":
  main()

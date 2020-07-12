import json
import requests
import re
import whois
from pyfaup.faup import Faup
import sys
import codecs
import datetime
import smtplib

key = ''
url = ''
timeframe='1d'
ignore_eventid = []
output_domain_file = '/tmp/possibledomains.txt'


def checkDomain(domain):
    response = requests.get("https://dns.google/resolve?name={}".format(domain))
    try:
        response_json = json.loads(response.text)
        if response_json['Status'] != 0:
            return True
        return False
    except:
        return False


def getmisp_domains(key, url, timeframe):
    response_domains = []
    headers = {'Authorization': '{}'.format(key), 'Content-type': 'application/json', 'Accept': 'application/json'}
    payload = '{ "returnFormat": "json", "type": "domain", "last": "%s", "enforceWarninglist": true }' % timeframe
    response = requests.post(url, headers=headers, data=payload, verify=False)
    json_response = json.loads(response.text)
    fp = Faup()
    try:
        for attr in json_response['response']['Attribute']:
            url = attr['value']
            eventid = attr['event_id']
            if eventid not in ignore_eventid:
                fp.decode(url)
                domain = fp.get_domain()
                category = attr['category']
                timestamp = datetime.datetime.utcfromtimestamp(int(attr['timestamp'])).strftime('%Y-%m-%d')
                response_domains.append({'domain': domain, 'eventid': eventid, 'category': category, 'timestamp': timestamp})
        return response_domains
    except:
        return response_domains


def getmisp_urls(key, url, timeframe):
    response_domains = []
    headers = {'Authorization': '{}'.format(key), 'Content-type': 'application/json', 'Accept': 'application/json'}
    payload = '{ "returnFormat": "json", "type": "url", "last": "%s", "enforceWarninglist": true }' % timeframe
    response = requests.post(url, headers=headers, data=payload, verify=False)
    json_response = json.loads(response.text)
    fp = Faup()
    try:
        for attr in json_response['response']['Attribute']:
            url = attr['value']
            eventid = attr['event_id']
            if eventid not in ignore_eventid:
                category = attr['category']
                timestamp = datetime.datetime.utcfromtimestamp(int(attr['timestamp'])).strftime('%Y-%m-%d')
                fp.decode(url)
                domain = fp.get_domain()
                if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain):
                    response_domains.append({'domain': domain, 'eventid': eventid, 'category': category, 'timestamp': timestamp})

        return response_domains
    except:
        return response_domains


def inCheckRegister(domain, domainlist):
    for el in domainlist:
        if domain == el['domain']:
            return True
    return False


def checkRegister(domains):
    check_to_register = []
    if len(domains) > 0:
        for domain in domains:
            # First check the DNS
            if not inCheckRegister(domain['domain'], check_to_register) and checkDomain(domain['domain']):
                # Now check whois
                try:
                    whois_result = whois.query(domain['domain'])
                    if whois_result.creation_date is None:
                        check_to_register.append({'domain': domain['domain'], 'eventid': domain['eventid'], 'reason': 'No DNS. No Whois', 'category': domain['category'], 'timestamp': domain['timestamp']})
                except ValueError:
                    continue
                except Exception as e:
                    reason = str(e).split('\n')[0]
                    check_to_register.append({'domain': domain['domain'], 'eventid': domain['eventid'], 'reason': reason,  'category': domain['category'], 'timestamp': domain['timestamp']})

    return check_to_register


# Read all domains
#print(getmisp_urls(key, url, timeframe))
#print(getmisp_domains(key, url, timeframe))
res_urls = checkRegister(getmisp_urls(key, url, timeframe))
res_domains = checkRegister(getmisp_domains(key, url, timeframe))

message = "Subject: MISP Domains available for registration\n\n\n"
if len(res_urls) > 0:
    for domain in res_urls:
        message = message + json.dumps(domain) + "\n"
if len(res_domains) > 0:
    for domain in res_domains:
        message = message + json.dumps(domain) + "\n"

smtp_server = '127.0.0.1'
sender_email = 'MAIL_SENDER_RCPT'
with smtplib.SMTP(smtp_server) as server:
    server.sendmail(sender_email, sender_email, message)

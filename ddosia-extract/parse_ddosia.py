import urllib3
import sys
import json
import requests
import tldextract
from datetime import datetime

from pymisp import *

# Get events from MISP with the DDoSia configuration object.
# Extract unique hostnames and domains
# Optionally send to Mattermost
#
# Koen Van Impe - 2024

# Credentials
misp_url = "MISP"
misp_key = "KEY"
misp_verifycert = True
mattermost_hook = ""

# Output
target_hostnames = []
target_domains = []

# Send to Mattermost?
send_mattermost = False

# MISP organisation "witha.name"
query_org = "ae763844-03bf-4588-af75-932d5ed2df8c"

# Limit for recent events
date_filter = "1d"

# Create PyMISP object and test connectivity
misp = PyMISP(misp_url, misp_key, misp_verifycert)
print(f"Extract hostnames from {misp_url}")

# Search for events
events = misp.search("events", pythonify=True, org=query_org, published=True, date=date_filter)

# Process events
if len(events) > 0:
    print("Parsing {} events".format(len(events)))
    for event in events:
        print(" Event {} ({})".format(event.info, event.uuid))
        for object in event.objects:
            if object.name == "ddos-config":
                for attribute in object.Attribute:
                    if attribute.type == "hostname":
                        check_value = attribute.value.lower().strip()
                        if check_value not in target_hostnames:
                            target_hostnames.append(check_value)
                            print(f"  Found {check_value}")

                        extracted = tldextract.extract(check_value)
                        domain = '.'.join([extracted.domain, extracted.suffix])
                        if domain not in target_domains:
                            target_domains.append(domain)

    if len(target_hostnames) > 0:
        target_hostnames.sort()
        target_domains.sort()
        now = datetime.now()

        print("Parsed {} events and found {} unique hostnames for {} domains - ({})".format(len(events), len(target_hostnames), len(target_domains), now.date()))
        if send_mattermost:
            summary = "# Parsed {} events and found {} unique hostnames for {} domains - ({})\n\n## Hostnames\n\n".format(len(events), len(target_hostnames), len(target_domains), now.date())

        print("Hostnames")
        for t in target_hostnames:
            if send_mattermost:
                summary += "\n{}".format(t)
            print(f" {t}")

        print("Domains")
        if send_mattermost:
            summary += "\n## Domains\n\n"
        for t in target_domains:
            if send_mattermost:
                summary += "\n{}".format(t)
            print(f" {t}")

        if send_mattermost:
            summary += "\n"
            message = {"username": "witha.name-reporters", "text": summary}
            r = requests.post(mattermost_hook, data=json.dumps(message))
else:
    print("No events found.")

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
teams_hook = ""
ddosia_file_output = "/var/www/MISP/app/webroot/misp-export/ddosia.txt"

# Output
target_hostnames = []
target_domains = []

# Send to Mattermost?
send_mattermost = False

# Send to Teams
send_teams = False

# Write to file
write_to_ddosia_file_output = False

# MISP organisation "witha.name"
query_org = "ae763844-03bf-4588-af75-932d5ed2df8c"

# Published?
published = True

# Limit for recent events
date_filter = "1d"

# Create PyMISP object and test connectivity
misp = PyMISP(misp_url, misp_key, misp_verifycert)
print(f"Extract hostnames from {misp_url}")

# Search for events
events = misp.search("events", pythonify=True, org=query_org, published=published, date=date_filter)

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
        
        title = "DDoSia config: Parsed {} MISP events and found {} unique hostnames for {} domains - ({}, last {})".format(len(events), len(target_hostnames), len(target_domains), datetime.now().date(), date_filter)
        summary = "Hostnames\n------------\n"
        summary_md = "# Hostnames\n"

        for t in target_hostnames:
            summary += "\n{}".format(t)
            summary_md += "\n- {}".format(t)

        summary += "\n\nDomains\n----------\n"
        summary_md += "\n\n# Domains\n"
        for t in target_domains:
            summary += "\n{}".format(t)
            summary_md += "\n- {}".format(t)
        summary_md += "\n"
        
        if send_mattermost:
            summary_md = title + summary_md + "\n"
            message = {"username": "witha.name-reporters", "text": summary_md}
            r = requests.post(mattermost_hook, data=json.dumps(message))
            print(r, r.status_code, r.text)
                        
        if send_teams:
            message = {
                    "type": "message",
                    "attachments": [
                        {
                            "contentType": "application/vnd.microsoft.teams.card.o365connector",
                            "content": {
                                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                                "type": "MessageCard",
                                "context": "https://schema.org/extensions",
                                "title": title,
                                "version": "1.0",
                                "sections": [
                                    {
                                        "text": summary_md
                                    }
                                ]
                            }
                        }
                    ]
                }
            r = requests.post(teams_hook, json=message)
            
        if write_to_ddosia_file_output:
            summary = title + "\n\n" + summary + "\n"
            with open(ddosia_file_output, 'w') as file:
                file.write(summary)

else:
    print("No events found.")

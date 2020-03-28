#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Koen Van Impe

Create block list from MISP data
Put this script in crontab to run every /15 or /60
    */5 *    * * *   mispuser   /usr/bin/python3 /home/mispuser/PyMISP/examples/blocklist_generator.py


'''

from pymisp import ExpandedPyMISP
from keys import misp_url, misp_key, misp_verifycert

import logging
import os
import sys
import json
import urllib3


if misp_verifycert is False:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
misp = ExpandedPyMISP(misp_url, misp_key, misp_verifycert, debug=False, tool='blocklist_generator')
exclude_warninglist = "corp_exclusion"
path_to_warninglist = "/var/www/MISP/app/files/warninglists/lists/{}/list.json".format(exclude_warninglist)
output_full_csv = "covid19_domains.csv"
output_domainonly_csv = "covid19_domains_domainonly.csv"
misp_filter_tag = "pandemic:covid-19=\"cyber\""


def get_valid_domains():
    return ['belgium.be', 'google.com', 'www.info-coronavirus.be', 'info-coronavirus.be', '2020coronavirus.org']

# Step 0: Print all enabled warninglists
active_warninglists = misp.warninglists()
for w_list in active_warninglists:
    w_list_detail = w_list["Warninglist"]["name"]
    logging.info("Warninglist enabled {}".format(w_list_detail))

# Step 1: Fetch the list of "valid domains"
valid_domains = get_valid_domains()

# Step 2: Extend the exclusion list
domains_for_exclusion = []
for domain in valid_domains:
    # Check if the domain is already in a warninglist
    lookup_warninglist = misp.values_in_warninglist(domain)
    if lookup_warninglist:
        # It's already in the list, ignore
        res = lookup_warninglist[domain][0]
        list_name = lookup_warninglist[domain][0]['name']
        list_id = lookup_warninglist[domain][0]['id']
        logging.info("Ignore domain '{}' because already in {} (id {})".format(domain, list_name, list_id))
    else:
        # A new domain, add it to the exclusion list
        domains_for_exclusion.append(domain)
        logging.info("Add domain '{}'".format(domain))

# Step 3: Write the exclusion list
if domains_for_exclusion:
    # First read current file
    logging.info("Reading exclusion file")
    with open(path_to_warninglist) as exclusion_file:
        data = json.load(exclusion_file)

    exclusion_file_version = data["version"]
    current_list = data["list"]
    new_list = (current_list + domains_for_exclusion)
    new_list.sort()

    data["version"] = exclusion_file_version + 1
    data["list"] = new_list

    logging.info("Updating exclusion file")
    with open(path_to_warninglist, 'w') as exclusion_file:
        json.dump(data, exclusion_file)

# Step 4: Update the MISP warning lists
update_result = misp.update_warninglists()
logging.info(json.dumps(update_result))

# Step 5: Fetch all the domains that we want on the blocklist
relative_path = 'attributes/restSearch'
body = {
    "returnFormat": "csv",
    "enforceWarninglist": "true",
    "tags": misp_filter_tag,
    "limit": "5",
    "type": ["url", "domain", "hostname"]
    }
result_full = misp.direct_call(relative_path, body)
result_domainonly = ""
step1 = True
for el in result_full.split('\n'):
    if step1 is True:
        step1 = False
        continue
    if el:
        domain = el.split(",")[4].replace('"', '')
        result_domainonly = result_domainonly + "\n{}".format(domain)

# Step 6: Write the blocklist
logging.info("Write {}".format(output_full_csv))
f = open(output_full_csv, "w")
f.write(result_full)

logging.info("Write {}".format(output_domainonly_csv))
f = open(output_domainonly_csv, "w")
f.write(result_domainonly)

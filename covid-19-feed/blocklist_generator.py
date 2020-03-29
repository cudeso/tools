#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Koen Van Impe

Create block list from MISP data
Put this script in crontab to run every /15 or /60
    */30 *    * * *   root   /var/www/MISP/venv/bin/python3 /var/www/MISP/PyMISP/examples/blocklist_generator.py


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


def get_valid_domains():
    return ['belgium.be', 'google.com', 'www.info-coronavirus.be', 'info-coronavirus.be']


def fetch_misp_results(misp_tags):
    relative_path = 'attributes/restSearch'
    body = {
        "returnFormat": "json",
        "enforceWarninglist": "True",
        "tags": misp_tags,
        "type": ["url", "domain", "hostname"],
        "includeDecayScore": "True",
        "includeEventTags": "True"
        }
    result = misp.direct_call(relative_path, body)

    result_csv = result_tlpwhite_csv = result_falsepositive_low = result_domain_csv =  result_domain_tlpwhite_csv = result_domain_falsepositive_csv = "value,decay_sore,value_type,event_id,event_info"
    if "Attribute" in result:

        for attribute in result["Attribute"]:
            value = attribute["value"]
            value_type = attribute["type"]
            decay_score = 0
            if "decay_score" in attribute:
                decay_score = attribute["decay_score"][0]["score"]
            event_info = attribute["Event"]["info"]
            event_id = attribute["Event"]["id"]
            result_csv = result_csv + "\n{},{},{},{},\"{}\"".format(value, decay_score, value_type, event_id, event_info)
            result_domain_csv = result_domain_csv + "\n{}".format(value)

            for t in attribute["Tag"]:
                if t["name"] == "tlp:white":
                    result_tlpwhite_csv = result_tlpwhite_csv + "\n{},{},{},{},\"{}\"".format(value, decay_score, value_type, event_id, event_info)
                    result_domain_tlpwhite_csv = result_domain_tlpwhite_csv + "\n{}".format(value)
                if t["name"] == "false-positive:risk=\"low\"":
                    result_falsepositive_low = result_falsepositive_low + "\n{},{},{},{},\"{}\"".format(value, decay_score, value_type, event_id, event_info)
                    result_domain_falsepositive_csv = result_domain_falsepositive_csv + "\n{}".format(value)

    return result_csv, result_tlpwhite_csv, result_falsepositive_low, result_domain_csv, result_domain_tlpwhite_csv, result_domain_falsepositive_csv

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
    lookup_warninglist = misp.values_in_warninglist([domain])
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
result_full, result_tlpwhite, result_fp, result_domain, result_domain_tlpwhite, result_domain_fp = fetch_misp_results("pandemic:covid-19=\"cyber\"")

# Step 6: Write the blocklist
logging.info("Write CSV files")
f = open("/home/misp/blocklist_upload/blocklist_full.csv", "w")
f.write(result_full)
f = open("/home/misp/blocklist_upload/blocklist_tlpwhite.csv", "w")
f.write(result_tlpwhite)
f = open("/home/misp/blocklist_upload/blocklist_fp_lowrisk.csv", "w")
f.write(result_fp)
f = open("/home/misp/blocklist_upload/blocklist_domain.csv", "w")
f.write(result_domain)
f = open("/home/misp/blocklist_upload/blocklist_domain_fp_lowrisk.csv", "w")
f.write(result_domain_fp)
f = open("/home/misp/blocklist_upload/blocklist_domain_tlpwhite.csv", "w")
f.write(result_domain_tlpwhite)
import sys
import pandas as pd
from Evtx.Evtx import Evtx
import xml.etree.ElementTree as ET

from collections import defaultdict
from urllib.parse import urlparse

from pymisp import *
import urllib3


'''
Extract DNS events from an EVTX file and parse the relevant fields. Check the hostnames and domains against MISP.

Koen Van Impe

'''


def extract_domain(domain):
    parts = domain.strip(".").split(".")
    if len(parts) > 2:
        return ".".join(parts[-2:])
    return domain.strip(".")


def check_misp(value):
    misp_url = "https://misp"
    misp_key = "MISP_API_KEY"
    misp_verifycert = False

    if misp_key != "MISP_API_KEY" and value:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        misp = PyMISP(misp_url, misp_key, misp_verifycert)
        result = misp.search(value=value, to_ids=True, pythonify=True, limit=1)
        if len(result) > 0:
            return True
        return False
    return False


def parse_dns_evtx(evtx_file, recordlimit=None):
    events = []
    queries = {}
    recordcount = 0
    try:
        with Evtx(evtx_file) as log:
            for record in log.records():
                try:
                    xml_str = record.xml()
                    root = ET.fromstring(xml_str)

                    namespace = "{http://schemas.microsoft.com/win/2004/08/events/event}"

                    timestamp_element = root.find(f".//{namespace}TimeCreated")
                    timestamp = timestamp_element.attrib["SystemTime"] if timestamp_element is not None else "N/A"

                    event_id_element = root.find(f".//{namespace}EventID")
                    event_id = event_id_element.text if event_id_element is not None else "N/A"

                    computer_element = root.find(f".//{namespace}Computer")
                    computer = computer_element.text if computer_element is not None else "N/A"

                    source_ip = None
                    qname = None

                    for data in root.findall(f".//{namespace}EventData/{namespace}Data"):
                        if "Name" in data.attrib:
                            if data.attrib["Name"] == "Source":
                                source_ip = data.text
                            elif data.attrib["Name"] == "QNAME":
                                qname = data.text

                    if event_id != "N/A" and timestamp != "N/A" and computer != "N/A" and source_ip and qname:
                        if queries.get(qname, False):
                            queries[qname] += 1
                        else:
                            queries[qname] = 1

                        events.append({
                            "EventID": event_id,
                            "TimeCreated": timestamp,
                            "Computer": computer,
                            "Source": source_ip,
                            "QNAME": qname
                        })

                except ET.ParseError:
                    print("Error parsing XML event, skipping...")
                except Exception as e:
                    print(f"Skipping event due to error: {e}")

                recordcount += 1
                if recordlimit:
                    if recordcount >= recordlimit:
                        break

        if events:
            df = pd.DataFrame(events)
            print(df)
            df.to_csv("dns_events.csv", index=False, mode="w")
            print("\n\n")

            sorted_queries = dict(sorted(queries.items(), key=lambda item: item[1], reverse=True))
            df = pd.DataFrame(sorted_queries.items(), columns=["Hostname", "Count"])
            df["MISP_Check"] = df["Hostname"].apply(check_misp)
            df.to_csv("dns_hostnames.csv", index=False, mode="w")
            print("Sorted hostnames:")
            print(df.to_string(index=False))

            print("\n\n")
            merged_queries = defaultdict(int)
            for query, count in queries.items():
                domain = extract_domain(query)
                merged_queries[domain] += count
            sorted_merged_queries = dict(sorted(merged_queries.items(), key=lambda item: item[1], reverse=True))
            df = pd.DataFrame(sorted_merged_queries.items(), columns=["Domain", "Count"])
            df["MISP_Check"] = df["Domain"].apply(check_misp)
            df.to_csv("dns_domains.csv", index=False, mode="w")
            print("Sorted domains:")
            print(df.to_string(index=False))

        else:
            print("No relevant DNS events found in the EVTX file.")

    except Exception as e:
        print(f"Failed to process EVTX file: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python parse_dns_evtx.py <path_to_evtx_file> [recordlimit]")
    else:
        evtx_file_path = sys.argv[1]
        recordlimit = int(sys.argv[2]) if len(sys.argv) == 3 and sys.argv[2].isdigit() else None
        parse_dns_evtx(evtx_file_path, recordlimit)

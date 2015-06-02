#!/usr/bin/env python 

# Test Logjam vulnerable hosts 
# https://weakdh.org/sysadmin.html (similar to Qualys SSLlabs but easier to parse)
#
# Koen Van Impe 20150528
#
#   Ask the people of weakdh.org for permission before scanning
#

import json
import urllib2
import time

weakdh_hosts = "weakdh.hosts"
pause_interval = 5
base_url = "https://weakdh.org/check/?server="

f = open( weakdh_hosts , 'r')
count = 0
vulnerable = 0
with_tls = 0
no_result = 0
verbose = False
for host in f:
    count = count + 1
    host = host.strip()
    response = urllib2.urlopen( base_url + host )
    json_data = json.load(response) 

    host = json_data["domain"]
    ip = json_data["ip_addresses"][0]
    has_tls = json_data["results"][0]["has_tls"]

    if has_tls:
        error = json_data["results"][0]["error"]
        if not error:
            with_tls = with_tls + 1
            try:
                prime_length = json_data["results"][0]["dh_params"]["prime_length"]
                export_dh_params = json_data["results"][0]["export_dh_params"]["prime_length"]
                if prime_length < 1024:
                    print ip, host, "Vulnerable"
                    vulnerable = vulnerable + 1
                elif export_dh_params < 1024:
                    print ip, host, "Vulnerable"
                    vulnerable = vulnerable + 1
                else:
                    if verbose:
                        print ip, host, " has TLS, not vulnerable"
            except:
                continue
        else:
            no_result = no_result + 1
            if verbose:
                print ip, host, " no result from weakDH"
    else:
        if verbose:
            print ip, host, "no TLS"
    time.sleep( pause_interval )
print "%s hosts tested, %s with no results, %s sites with TLS, %s vulnerable" % (count, no_result, with_tls, vulnerable)



#!/usr/bin/python

# Get IP prefixes per country
#
# Koen Van Impe 20160219
#
# Sourced from http://blog.erben.sk/2014/01/28/generating-country-ip-ranges-lists/
#
# Usage : ./ip_per_country_ripe.py BE

import math
import urllib
import sys

country = sys.argv[1]

opener = urllib.FancyURLopener()
f = opener.open("ftp://ftp.ripe.net/pub/stats/ripencc/delegated-ripencc-latest")
lines=f.readlines()

for line in lines:
        if (('ipv4' in line) & (country in line)) :
                s=line.split("|")
                net=s[3]
                cidr=float(s[4])
                print "%s/%d" % (net,(32-math.log(cidr,2)))
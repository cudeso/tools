#!/usr/bin/python
# encoding: utf-8

# Extract IP coordinates from EXIF data for VPNFilter 
# Koen Van Impe - 20180525
# See: https://securelist.com/vpnfilter-exif-to-c2-mechanism-analysed/85721/

from ctypes import c_uint8;
import exifread
import sys

f = open( sys.argv[1] , 'rb')
tags = exifread.process_file(f)

octet_1_2_fixed = 90  # 0x5A
octet_3_4_fixed = 180 # 0xB4

for tag in tags.keys():
  if tag == 'GPS GPSLongitude':
     gps_long = tags[tag]
     o3p2 = int(str(gps_long.__dict__["values"][0]))
     o3p1 = int(str(gps_long.__dict__["values"][1]))
     o4p1 = int(str(gps_long.__dict__["values"][2]))
  elif tag == 'GPS GPSLatitude':
     gps_lat = tags[tag]
     o1p2 = int(str(gps_lat.__dict__["values"][0]))
     o1p1 = int(str(gps_lat.__dict__["values"][1]))
     o2p1 = int(str(gps_lat.__dict__["values"][2]))

octet_1 = c_uint8( o1p1 + (o1p2 + octet_1_2_fixed) )
octet_2 = c_uint8( o2p1 + (o1p2 + octet_1_2_fixed) )
octet_3 = c_uint8( o3p1 + (o3p2 + octet_3_4_fixed) )
octet_4 = c_uint8( o4p1 + (o3p2 + octet_3_4_fixed) )

print "GPS Long/Lat : %s / %s" % (str(gps_long), str(gps_lat))
print "C2 IP: %u.%u.%u.%u" % (octet_1.value, octet_2.value, octet_3.value, octet_4.value)

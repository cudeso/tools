#!/usr/bin/python


import argparse
from scapy.all import *

parser = argparse.ArgumentParser()
parser.add_argument("--src", "--source-ip", help="Replace SOURCE IP address", default="0.0.0.1")
parser.add_argument("--dst", "--dst-ip", help="Replace DESTINATION IP address", default="0.0.0.255")
parser.add_argument("--pcap", help="PCAP file to read", default="cap.pcap")
parser.add_argument("--out", help="PCAP file to write", default="out.pcap")
parser.add_argument("--ports", help="Anonimize ports, default NO", action="store_true")
parser.add_argument("--verbose", help="increase output verbosity",
                    action="store_true")
args = parser.parse_args()

try:
	with open(args.pcap) as file:
		pass
		if args.verbose:
			print "Reading pcap file", args.pcap
		pcap = rdpcap(args.pcap)
		for p in pcap:
			if args.verbose: 
				print "Replace source IP: ", p[IP].src, " with ", args.src
				print "Replace dest   IP: ", p[IP].dst, " with ", args.dst
			p[IP].src = args.src 
			p[IP].dst = args.dst
		wrpcap(args.out, pcap)

except IOError as e:
	print "Unable to open pcap file" 

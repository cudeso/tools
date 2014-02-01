#!/bin/bash

# Koen Van Impe - 20140201
# 
# Fetch different blocklists to be used by iptables blocking
#

BLOCKLIST_NETWORK=blocklist-network
BLOCKLIST_IP=blocklist-ip

TMP_LOG="$(mktemp)"
TMP_OUTPUT="$(mktemp)"
TMP_OUTPUT2="$(mktemp)"

wget --output-file=$TMP_LOG --output-document=$TMP_OUTPUT  http://www.spamhaus.org/drop/edrop.txt 
logger "Downloaded edrop.txt"
tail -n +5 $TMP_OUTPUT | awk '{print $1;}' > $TMP_OUTPUT2 
echo > $TMP_OUTPUT
wget --output-file=$TMP_LOG --output-document=$TMP_OUTPUT  http://www.spamhaus.org/drop/drop.txt 
logger "Downloaded drop.txt"
tail -n +5 $TMP_OUTPUT | awk '{print $1;}' >> $TMP_OUTPUT2 
cat $TMP_OUTPUT2 | sort -n > $BLOCKLIST_NETWORK
echo > $TMP_OUTPUT
echo > $TMP_OUTPUT2

wget --output-file=$TMP_LOG --output-document=$TMP_OUTPUT http://lists.blocklist.de/lists/ssh.txt 
logger "Downloaded ssh.txt"
cat $TMP_OUTPUT > $TMP_OUTPUT2
wget --output-file=$TMP_LOG --output-document=$TMP_OUTPUT http://www.openbl.org/lists/base_all_ssh-only.txt 
logger "Downloaded base_all_ssh.txt"
tail -n +5 $TMP_OUTPUT >> $TMP_OUTPUT2 
cat $TMP_OUTPUT2 | sort -n > $BLOCKLIST_IP

rm $TMP_LOG
rm $TMP_OUTPUT
rm $TMP_OUTPUT2 

logger "Blocklists available $BLOCKLIST_IP / $BLOCKLIST_NETWORK"

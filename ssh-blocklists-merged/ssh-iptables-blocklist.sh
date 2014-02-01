#!/bin/sh

# Koen Van Impe - 20140201
# 
# Import blocklists into iptables 
#

# Instead of adding the IPs individually, use 
#  http://ipset.netfilter.org/
# for better performance

IPTABLES=/sbin/iptables
PUB_INTERFACE=eth0

BLOCKLIST_NETWORK=blocklist-network
BLOCKLIST_IP=blocklist-ip

BLOCKLIST_CHAIN=sshblocklist

$IPTABLES -N $BLOCKLIST_CHAIN
$IPTABLES -F $BLOCKLIST_CHAIN

for i in `cat $BLOCKLIST_NETWORK`; do $IPTABLES -A $BLOCKLIST_CHAIN -i $PUB_INTERFACE -s $i -p tcp --dport 22 -j LOG --log-prefix " Drop blocklist"; $IPTABLES -A $BLOCKLIST_CHAIN -i $PUB_INTERFACE -s $i -p tcp --dport 22 -j DROP; done 
logger "Blocklist-network iptables rules added"
for i in `cat $BLOCKLIST_IP`; do $IPTABLES -A $BLOCKLIST_CHAIN -i $PUB_INTERFACE -s $i -p tcp --dport 22 -j LOG --log-prefix " Drop blocklist"; $IPTABLES -A $BLOCKLIST_CHAIN -i $PUB_INTERFACE -s $i -p tcp --dport 22 -j DROP; done 
logger "Blocklist-ip iptables rules added"


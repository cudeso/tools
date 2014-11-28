# Initscript for ulogd2

Adjusted init script for ulogd2.

Ulogd init script with option to exclude a list of IPs being logged
 http://www.netfilter.org/projects/ulogd/

# Prerequisites

## Jump to the correct chain

Make sure that the first rule in the INPUT chain redirects the traffic to the new chain defined in **IPTABLES_CHAIN**.
The default chain is **ULOGD_exclude**.

'''
iptables -I INPUT -j ULOGD_exclude
'''

## List of IPs

The list of IPs that need to be excluded is saved in **ULOGD_EXCLUDE**.
The default file is **/etc/ulogd.excludeip** and needs to have a network / ip per line.

'''
'''

# Changes compared to the original script

There's an extra function **do_iptables** that parces the file with IPs and creates iptables rules. The function is called from the start, restart and reload function.

'''
 #
 # Function to setup an iptables chain with exclusion IPs 
 #
do_iptables() {
        ULOGD_EXCLUDE="/etc/ulogd.excludeip"
        IPTABLES_CHAIN="ULOGD_exclude"
        if [ -f $ULOGD_EXCLUDE ]; then
                iptables -N $IPTABLES_CHAIN
                iptables -F $IPTABLES_CHAIN
                while read IP 
                do
                    if [ ! -z $IP ]; then
                                echo "Exclude traffic for $IP"
                                iptables -I $IPTABLES_CHAIN -j NFLOG --nflog-group 1 --nflog-threshold 20 ! -s $IP
                        fi
                done < $ULOGD_EXCLUDE
        fi
}
'''
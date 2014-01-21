#!/bin/bash

# Simple nc listener
# Koen Van Impe
#
# Remember that nc does not trap the remote-IP
# use a tcpdump -w next to this listener
#

runs=0
port=$1
output="nc-capture.txt"
input="nc-input.txt"

if [[ $port -gt 0 ]]; then
  while true
  do
    date=`date '+%Y%m%d%H%M%S'`
    outputfile="$date-$output"
    runs=$((runs+1))
    echo "Starting run $runs on port $port, output to $outputfile"
    echo "$date - tcp/$port" >> $outputfile
    echo "=========================================" >> $outputfile
    nc -l -p $port >> $outputfile < $input 
  done
else
  echo "No port specified"
fi

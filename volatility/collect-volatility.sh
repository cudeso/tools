#!/bin/bash
# Script to collect information by utilizing volatility

# v0.3 - Updated to include mftparser
#        - Added a temp directory
# v0.2 - Updated the DKOM section to include the 3 columns and not just the 1st.

#To come...
#Analyze specific registry keys that aide in an investigation

####  Configurable Settings #############
homeDir='/home/volatility/image'
memImage="$homeDir/image.vmem"
locVolPy='/usr/share/volatility/vol.py'
volProfile=''
#########################################

outputDir="$homeDir/output"
dumpDir="$homeDir/dumpdir"
tempDir="$homeDir/temp"

if [ ! -d $outputDir ]; then
    mkdir $outputDir
    mkdir $dumpDir
    mkdir $tempDir
fi

# Find the profile for the image that is being analyzed and store it in volProfile
python $locVolPy -f $memImage imageinfo > $outputDir/imageinfo
cat $outputDir/imageinfo | grep "Suggested Profile(s)" | awk '{print "Identified Profile: " $4}' | sed 's/,//'
volProfile=`cat $outputDir/imageinfo | grep "Suggested Profile(s)" | awk '{print $4}' | sed 's/,//'`


echo "Running pslist and saving results to $outputDir/pslist"
python $locVolPy -f $memImage --profile=$volProfile pslist > $outputDir/pslist
echo "Running pstree and saving results to $outputDir/pstree"
python $locVolPy -f $memImage --profile=$volProfile pstree > $outputDir/pstree
echo "Running psscan and saving results to $outputDir/psscan"
python $locVolPy -f $memImage --profile=$volProfile psscan > $outputDir/psscan
echo "Running psxview and saving results to $outputDir/psxview"
python $locVolPy -f $memImage --profile=$volProfile psxview > $outputDir/psxview

echo "Find processes in psxview that is using Direct Kernel Object Manipulation (DKOM)"
echo "Display from psxview any processes with "False" in the psscan, pslist, thrdproc"
echo "Find processes in psxview that is using Direct Kernel Object Manipulation (DKOM)" > $outputDir/possibleDKOM
echo "Display from psxview any processes with "False" in the psscan, pslist, thrdproc" >> $outputDir/possibleDKOM
while read line
do
    pslistColumn=`echo $line | awk '{print $4}'`
    psscanColumn=`echo $line | awk '{print $5}'`
    thrdprocColumn=`echo $line | awk '{print $6}'`
    if [ $pslistColumn == 'False' ]; then
        echo "Found: $line" >> $outputDir/possibleDKOM
    fi
    if [ $psscanColumn == 'False' ]; then
        echo "Found: $line" >> $outputDir/possibleDKOM
    fi
    if [ $thrdprocColumn == 'False' ]; then
        echo "Found: $line" >> $outputDir/possibleDKOM
    fi
done < $outputDir/psxview
echo

echo "Running connections and saving results to $outputDir/connections"
python $locVolPy -f $memImage --profile=$volProfile connections > $outputDir/connections
echo "Running connscan and saving results to $outputDir/connscan"
python $locVolPy -f $memImage --profile=$volProfile connscan > $outputDir/connscan
echo "Running filescan and saving results to $outputDir/filescan"
python $locVolPy -f $memImage --profile=$volProfile filescan > $outputDir/filescan
echo "Running iehistory and saving results to $outputDir/iehistory"
python $locVolPy -f $memImage --profile=$volProfile iehistory > $outputDir/iehistory
echo "Running cmdscan and saving results to $outputDir/cmdscan"
python $locVolPy -f $memImage --profile=$volProfile cmdscan > $outputDir/cmdscan
echo "Running consoles and saving results to $outputDir/consoles"
python $locVolPy -f $memImage --profile=$volProfile consoles > $outputDir/consoles
echo "Running mftparser and saving results to $outputDir/mftpparser"
python $locVolPy -f $memImage --profile=$volProfile mftparser --output=body --output-file=$outputDir/mftparser.csv
mactime -b $outputDir/mftparser.csv -d -z UTC-6 > $outputDir/mftparserMactime.csv
echo "Running hivelist and saving results to $outputDir/hivelist"
python $locVolPy -f $memImage --profile=$volProfile hivelist > $outputDir/hivelist

echo "Saving the results of the hashdump to $outputDir/hashdump"
# Find the virtual address of the SYSTEM hive
while read line
do
    if [[ $line == *YSTEM* ]]; then
        systemVAddr=`echo $line | awk '{print $1}'`
    fi
done < $outputDir/hivelist
# Find the virtual address of the SAM hive
while read line
do
    if [[ $line == *SAM* ]]; then
        samVAddr=`echo $line | awk '{print $1}'`
    fi
done < $outputDir/hivelist
python $locVolPy -f $memImage --profile=$volProfile -y $systemVAddr -s $samVAddr hashdump > $outputDir/hashdump
# Output the accounts with blank passwords...

echo "Running malfind and saving results to $outputDir/malfind"
python $locVolPy -f $memImage --profile=$volProfile malfind --dump-dir $dumpDir > $outputDir/malfind
echo


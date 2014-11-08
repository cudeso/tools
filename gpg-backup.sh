#!/bin/bash
# Script to copy sensitive files
#
#   Files are put in an archive and then GPG protected
#   Put this script in a crontab
#       30  21  *   *   *   /Users/me/Scripts/gpg-backup.sh > /dev/null 2>&1
#
#   Koen Van Impe   20141108
#

BACKUP_HOST="<hostname>"
BACKUP_USER="<username>"
BACKUP_KEY="<privatekey>"
BACKUP_PATH="<pathtobackupto>"
GPG_RECIPIENT="<gpgRCPT>"
GPG_OUTPUT="backup.tar.gz.gpg"
# add $(date +%Y-%m-%d) to GPG_OUTPUT for unique backups
declare -a FILES=( '/home/user/.gnupg/'
                   '/home/user/.ssh/' )

if [ ${#FILES[@]} -gt 0 ]
then
    if [ -f $BACKUP_KEY ]
    then
        # Check SSH connection
        ssh -q -o "BatchMode=yes" -i $BACKUP_KEY $BACKUP_USER@$BACKUP_HOST "echo 2>&1"
        CONN=$?
        if [ $CONN == 0 ]
        then
            # Build up filelist to backup
            for file in "${FILES[@]}" 
            do
                BACKUP_FILES="$BACKUP_FILES $file"
            done
            rm $GPG_OUTPUT
            tar -cz $BACKUP_FILES | gpg --encrypt --recipient $GPG_RECIPIENT > $GPG_OUTPUT
            scp -i  $BACKUP_KEY $GPG_OUTPUT $BACKUP_USER@$BACKUP_HOST:$BACKUP_PATH/
            rm $GPG_OUTPUT
        else
            echo "SSH connection to $BACKUP_HOST failed"
        fi
    else
        echo "Private key $BACKUP_KEY not found"
    fi
else
    echo "No files to backup"
fi
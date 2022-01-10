# Backup virtual machines running on an ESXi server

## Setup

1. Add an extra datastore in VMWare ESXi. For example an NFS volume.
1. Enable SSH to ESXi server
1. Add the script (for example in /opt/cudeso)
1. Do the inline configuration
1. Make the script executable `chmod +x backup-vms.sh`
1. Make a copy of crontab `cp /var/spool/cron/crontabs/root /opt/cudeso/crontab`
1. Update crontab `vi /var/spool/cron/crontabs/root` and add a new entry
1. Get the PID for the crond `cat /var/run/crond.pid`
1. Restart crond `/usr/lib/vmware/busybox/bin/busybox crond`

## Caveats

* Unfortunatley VMWare ESXi does not support rsync (at least not natively). This would have made backups much easier.
* This assumes all the VM files (extra disks) are in the folder of the VM
* Avoid using spaces in the VM name
* Try the script first manually before putting it in crontab
* Tested on **ESXi 7.0.2**

## Script workflow

1. Find all "directories" in the datastore folder (basically list all VMs)
1. Create a backup directory
1. Copy base files
1. Create a new snapshot "backup"
1. Backup (and shrink) all the VMDKs
1. Remove the snapshot
1. Create a tar archive

# Sources

* [https://www.virten.net/2016/04/backup-solutions-for-free-esxi/](https://www.virten.net/2016/04/backup-solutions-for-free-esxi/)
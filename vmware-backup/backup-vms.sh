#!/bin/sh

# Backup VMs on ESXi
# Koen Van Impe - Inspired by https://www.virten.net/2016/04/backup-solutions-for-free-esxi/

SRC="/vmfs/volumes/datastore1"
DST="/vmfs/volumes/mynas.mydomain/esxi-03"

vm_backup()
{
	VM=$1

	# Create directory for backup
	mkdir -p "$DST/$VM"
	rm -f "$DST/$VM/"*

	# Copy base files
	cp -p "$SRC/$VM/"*.vmx "$DST/$VM/"
	cp -p "$SRC/$VM/"*.nvram "$DST/$VM/"
	cp -p "$SRC/$VM/"*.vmsd "$DST/$VM/"
	cp -p "$SRC/$VM/"*.log "$DST/$VM/"

	# Create a new snapshot
	vmid=$(vim-cmd vmsvc/getallvms | grep "$VM" | awk '{print $1}')
	vim-cmd vmsvc/snapshot.create $vmid backup 'Snapshot created by Backup Script' 0 0

	# Backup (and shrink) the disk
	find "$SRC/$VM/"*.vmdk  -type f | while read -r f ; do
  		base=$(basename "$f")
  		vmkfstools -i "$f" "$DST/$VM/$base" -d thin
	done

	# Remove the snapshot
	vmsnapshotid=$(vim-cmd vmsvc/snapshot.get $vmid | grep "Snapshot Id" | tail -n 1 | cut -d ':' -f 2)
	vim-cmd vmsvc/snapshot.remove $vmid $vmsnapshotid

	# Create a tar archive
	tar -zcf "$DST/$VM.tar.gz" "$DST/$VM/*"
}

find "$SRC/" -type d | while read -r f ; do
	vm_tmp=$(basename "$f")
	vm="$vm_tmp"
	if [ -n "$vm" ] && [ "$vm" != ".sdd.sf" ] && [ "$vm" != "datastore1" ] && [ "$vm" != "images" ]; then
		vm_backup "$vm"
	fi
done

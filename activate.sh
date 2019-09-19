#!/bin/bash
FUSER=$(fuser -vm /mnt/usb_share/ 2>&1 | wc -l)
if [ "$FUSER" == "2" ]; then
	umount /mnt/usb_share
	sleep 1
	sudo modprobe g_mass_storage file=/home/pi/usbdisk.img stall=0 ro=0 removable=1
	# TODO: change connected file system dynamically
	#modprobe g_mass_storage stall=0 removable=y
else
	echo "BUSY"
fi


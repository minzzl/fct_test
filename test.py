minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~$ lsmod | grep nvidia
minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~$ dmesg | grep -i nvidia
dmesg: read kernel buffer failed: Operation not permitted
minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~$ sudo dkms autoinstall
[sudo] password for minzzl: 
minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~$ sudo modprobe nvidia
modprobe: ERROR: could not insert 'nvidia': Key was rejected by service

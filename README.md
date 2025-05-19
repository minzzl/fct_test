# U-Boot
tftp 80000 Image

###################################################
bootcmd, bootargs 설정
###################################################

setenv bootcmd 'tftp 80000 Image; tftp 3100000 wt2837.dtb; tftp 3200000 ext2img.gz;	booti 80000 - 3100000'
setenv bootargs 'console=ttyS0,115200n81'
saveenv

###################################################
bootargs 설정 (루트 파일시스템 정보 포함)
###################################################

setenv bootargs 'console=ttyS0,115200n81 rootfstype=ext2 root=/dev/ram0 rw initrd=0x3200000,128M'
saveenv

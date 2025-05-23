root@WT2837:~# fdisk -l /dev/mmcblk0
Disk /dev/mmcblk0: 486 MB, 510132224 bytes, 996352 sectors
7784 cylinders, 4 heads, 32 sectors/track
Units: cylinders of 128 * 512 = 65536 bytes

Device       Boot StartCHS    EndCHS        StartLBA     EndLBA    Sectors  Size Id Type
/dev/mmcblk0p1    64,0,1      1023,3,32         8192     532479     524288  256M  c Win95 FAT32 (LBA)
/dev/mmcblk0p2    1023,3,32   1023,3,32       532480     895999     363520  177M 83 Linux
root@WT2837:~# df
Filesystem           1K-blocks      Used Available Use% Mounted on
/dev/root               126931     46228     74150  38% /
devtmpfs                322768         0    322768   0% /dev
tmpfs                   425648         0    425648   0% /dev/shm
tmpfs                   425648        28    425620   0% /tmp
tmpfs                   425648        16    425632   0% /run
root@WT2837:~# ls /mnt/sd
root@WT2837:~# mount -t ext4 /dev/m 
mem        mmcblk0    mmcblk0p1  mmcblk0p2  mydev      
root@WT2837:~# mount -t ext4 /dev/mmcblk0p
mmcblk0p1  mmcblk0p2  
root@WT2837:~# mount -t ext4 /dev/mmcblk0p2 /mnt/sd
[ 5589.968759] EXT4-fs (mmcblk0p2): recovery complete
[ 5589.975592] EXT4-fs (mmcblk0p2): mounted filesystem 6bc12fe4-b156-47bb-af2a-b0f6559414f3 r/w with ordered data mode. Quota mode: none.
root@WT2837:~# df
Filesystem           1K-blocks      Used Available Use% Mounted on
/dev/root               126931     46228     74150  38% /
devtmpfs                322768         0    322768   0% /dev
tmpfs                   425648         0    425648   0% /dev/shm
tmpfs                   425648        28    425620   0% /tmp
tmpfs                   425648        16    425632   0% /run
/dev/mmcblk0p2          170388        14    157651   0% /mnt/sd
root@WT2837:~# ls /mnt/sd/
lost+found
root@WT2837:~# 

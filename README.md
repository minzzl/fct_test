setenv Image 'tftp 80000 Image; fatwrite mmc 0:1 80000 Image ${filesize}'
setenv DTB 'tftp 80000 my2837.dtb; fatwrite mmc 0:1 80000 my2837.dtb ${filesize}'
setenv RFS 'tftp 80000 ext2img.gz; fatwrite mmc 0:1 80000 ext2img.gz ${filesize}'
setenv bootcmd 'fatload mmc 0:1 80000 Image; fatload mmc 0:1 3100000 my2837.dtb; fatload mmc 0:1 3200000 ext2img.gz; booti 80000 - 3100000'
saveenv
run Image # Kernel 이미지
run DTB # DTB 이미지
run RFS # RFS 이미지

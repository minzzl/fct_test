# 파티션이 마운트돼 있다면 먼저 해제
sudo umount /dev/mmcblk0p2

# /mnt/nfs/ext4g 이미지를 SD카드 2번 파티션에 기록
sudo dd if=/mnt/nfs/ext4g of=/dev/mmcblk0p2 bs=4M conv=fsync status=progress
# 1. 부트 아규먼트 갱신
setenv bootargs 'console=ttyS0,115200 root=/dev/mmcblk0p2 rootfstype=ext4 rw rootwait'

# 2. 부트 명령에서 ext2img.gz 부분 삭제
setenv bootcmd 'fatload mmc 0:1 0x80000 Image; \
                fatload mmc 0:1 0x3100000 my2837.dtb; \
                booti 0x80000 - 0x3100000'

# 3. (선택) rootfs 업데이트용 함수 새로 정의
#  p2 시작 LBA = 0x8200  (예: 532480 / 512 = 0x8200)
#  p2 블록수    = 0x2C800 (예: 363520 / 512 = 0x2C800)
setenv RFS 'tftp ${loadaddr} rootfs.ext4; mmc dev 0; mmc write ${loadaddr} 0x8200 0x2C800'

saveenv      # 변경사항 영구 저장
reset        # 재부팅해서 정상 마운트 확인

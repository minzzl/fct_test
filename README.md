#!/bin/sh

echo "[S99jpegtofb] Starting jpegtofb slideshow..."

# NFS가 마운트될 시간 확보 (필요 시 sleep)
sleep 2

# jpegtofb 실행
/usr/bin/jpegtofb -s 1 /mnt/nfs/test_contents/*.jpg &

echo "[S99jpegtofb] Done."

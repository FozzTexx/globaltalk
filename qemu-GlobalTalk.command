#!/bin/bash
cd "$(dirname "$0")"

DISK=GlobalTalk_HD.img
CDROM=Sys7.1-GlobalTalk_Install.img

qemu-system-m68k \
    -M q800 \
    -m 128 \
    -bios Q800.ROM \
    -vnc :10 \
    -g 1152x870x8 \
    -drive file=pram.img,format=raw,if=mtd \
    -nic bridge,model=dp83932,mac=08:00:07:A2:A2:A2 \
\
    -device scsi-hd,scsi-id=0,drive=hd0 \
    -drive format=raw,media=disk,if=none,id=hd0,file="${DISK}" \

#    -device scsi-cd,scsi-id=3,drive=cd3 \
#    -drive format=raw,media=disk,if=none,id=cd3,file="${CDROM}" \

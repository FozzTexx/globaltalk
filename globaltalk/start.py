#!/usr/bin/env python3
#
# Copyright 2024 by Chris Osborn <fozztexx@fozztexx.com>
#
# This file is part of globaltalk.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License at <http://www.gnu.org/licenses/> for
# more details.

import argparse
import os
import subprocess
import json
import re
import struct

import globaltalk

QEMU_CONF_PREFIX = "/usr/local/etc/qemu"
GLOBALTALK_CONFIG = "GlobalTalk-config"

IP_PATTERN = "[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+"

def build_argparser():
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("hd_image", help="file to be used as the hard drive image")
  parser.add_argument("--cdrom", help="file to use as a cdrom image")
  parser.add_argument("--bridge", default="br0", help="name of bridge interface")
  parser.add_argument("--appletalk_zone", help="name of AppleTalk zone")
  parser.add_argument("--appletalk_number", type=int, help="number of AppleTalk network")
  parser.add_argument("--appletalk_hosts",
                      help="comma separated list of Apple Internet Router hosts")
  parser.add_argument("--ip_address", help="IP address to configure in MacTCP, as: x.x.x.x/m")
  parser.add_argument("--gateway", help="IP address of gateway router")
  parser.add_argument("--ethernet_mac", default="08:00:07:A2:A2:A2",
                      help="MAC address to assign to emulated ethernet interface")
  parser.add_argument("--dns_server", action="append",
                      help="IP address of DNS server to configure in MacTCP")
  parser.add_argument("--ram", default="128", help="Amount of RAM in emulated Mac")
  parser.add_argument("--vnc_port", default="::1:10", help="VNC port")
  parser.add_argument("--resolution", default="1152x870x8", help="Graphics resolution")
  parser.add_argument("--reset_pram", action="store_true", help="reset pram.img")
  return parser

def image_info(path):
  cmd = ["qemu-img", "info", "--output=json", path]
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
  pstr = process.stdout.read()
  process.stdout.close()
  if isinstance(pstr, bytes):
    pstr = str(pstr, "utf-8")
  return json.loads(pstr)

def create_thread_record(disk_path, cnid, filename):
  disk = HFSDisk(disk_path)
  disk.mount()

  # FIXME - make sure it's unique
  thread_path = f":{filename}2"
  cmd = ["hmkdir", thread_path]
  subprocess.run(cmd)
  disk.unmount()

  thread_file = MacFile(disk_path, thread_path)
  catalog = Catalog(disk)
  node = catalog.findNode((thread_file.catalogID, ""))
  sectorNum = catalog.sectorForNode(node[0])
  sector = bytearray(disk.readSector(sectorNum))
  pointer = (node[2] + 1) * -2
  offset = struct.unpack(">H", sector[pointer:pointer+2])[0]
  reclen = sector[offset]

  sector[offset+2:offset+6] = struct.pack(">I", cnid)
  pointer = offset+reclen+1
  pointer = (pointer + 1) // 2 * 2
  sector[pointer] = 0x04
  sector[pointer+14] -= 1
  sector[pointer+15+sector[pointer+14]] = 0
  disk.writeSector(sectorNum, sector)
  disk.stream.close()

  disk.mount()
  cmd = ["hrmdir", thread_path]
  subprocess.run(cmd)
  disk.unmount()

  return

def main():
  args = build_argparser().parse_args()

  # FIXME - get args from environment

  if not os.path.exists(os.path.join("/sys/class/net", args.bridge)):
    print(f"Interface {args.bridge} does not exist")
    exit(1)

  if args.ip_address and not re.match(f"^{IP_PATTERN}/[0-9]+$", args.ip_address):
    print("Invalid IP or netmask specified:", args.ip_address)
    exit(1)

  cmd = ["iptables", "-C", "FORWARD", "-p", "all", "-i", args.bridge, "-j", "ACCEPT"]
  status = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  if status.returncode:
    cmd[1] = "-A"
    status = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

  with open(os.path.join(QEMU_CONF_PREFIX, "bridge.conf"), "w") as f:
    print(f"allow {args.bridge}", file=f)

  hd_path = os.path.dirname(os.path.abspath(args.hd_image))
  pram_path = os.path.join(hd_path, "pram.img")

  if not os.path.exists(pram_path) or args.reset_pram:
    pram = bytearray([0] * 256)
    with open(pram_path, mode="wb") as f:
      f.write(pram)

  vnc_port = args.vnc_port
  if vnc_port[0] != ':':
    vnc_port = f":{vnc_port}"

  rom_path = os.path.join(hd_path, "Q800.ROM")
  cmd = [
    "qemu-system-m68k",
    "-M", "q800",
    "-m", f"{args.ram}",
    "-bios", rom_path,
    "-vnc", vnc_port,
    "-g", f"{args.resolution}",
    "-drive", f"file={pram_path},format=raw,if=mtd",
    "-nic", f"bridge,model=dp83932,mac=f{args.ethernet_mac}",
  ]

  info = image_info(args.hd_image)
  cmd.extend([
    "-device", "scsi-hd,scsi-id=0,drive=hd0",
    "-drive", f"format={info['format']},media=disk,if=none,id=hd0,file={args.hd_image}",
  ])

  if args.cdrom:
    info = image_info(args.cdrom)
    cmd.extend([
      "-device", "scsi-hd,scsi-id=3,drive=cd3",
      "-drive", f"format={info['format']},media=cdrom,if=none,id=cd3,file={args.cdrom}",
    ])

  if args.ip_address or args.dns_server:
    mtcp_prefs = MacFile(args.hd_image, ":System Folder:Preferences:MacTCP Prep")
    mtcp = MacTCP(mtcp_prefs.resourcePath)

    if args.ip_address:
      mtcp.setIPAddress(args.ip_address, gateway=args.gateway)

    if args.dns_server:
      mtcp.dns = []
      for dns in args.dns_server:
        values = dns.split(":")
        ip_address = values[0]
        if not re.match(f"^{IP_PATTERN}$", ip_address):
          print("Invalid IP address:", ip_address)
          exit(1)
        domain = "."
        if len(values) > 1:
          domain = values[1]
        mtcp.addDNS(ip_address, domain)

    mtcp.save()
    mtcp_prefs.save()

  if args.appletalk_zone or args.appletalk_number or args.appletalk_hosts:
    if not args.appletalk_zone:
      print("Must provide appletalk_zone")
      exit(1)
    if args.appletalk_number is None:
      print("Must provide appletalk_number")
      exit(1)
    if not args.appletalk_hosts:
      print("Must provide appletalk_hosts")
      exit(1)

    gt_conf = MacFile(args.hd_image, f":{GLOBALTALK_CONFIG}",
                      dataPath=os.path.join(hd_path, f"{GLOBALTALK_CONFIG}.bin"))
    airconf = AIRConfig(gt_conf.resourcePath)
    airconf.setRouterName(args.appletalk_zone)
    airconf.setZoneName(args.appletalk_zone)
    airconf.setZoneNumber(args.appletalk_number, args.appletalk_number)
    airconf.setHosts(args.appletalk_hosts.split(","))

    airconf.save()
    gt_conf.save()

    pref_file = MacFile(args.hd_image, ":System Folder:Extensions:Router")
    airprefs = AIRPrefs(pref_file.resourcePath)
    airprefs.setFilename(GLOBALTALK_CONFIG)
    airprefs.setCNID(gt_conf.catalogID)
    airprefs.setAutostart(True)
    airprefs.save()
    pref_file.save()

    create_thread_record(args.hd_image, gt_conf.catalogID, GLOBALTALK_CONFIG)

  subprocess.run(cmd)

  return

if __name__ == '__main__':
  exit(main() or 0)

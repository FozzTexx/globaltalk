#!/usr/bin/env python3
from macresource import MacResource
import rsrcdump
import struct
from dataclasses import dataclass
import argparse

ACFG_ZONE = ('STR#', 16384)
ACFG_HOST = ('acfg', 16385)
ACFG_NAME = ('STR ', 1003)
ACFG_PORT = ('port', 0)

ZONE_FORMAT = ">H"
HOST_FORMAT = ">IH"
PORT_FORMAT = ">HHHH"

class AIRConfig(MacResource):
  def __init__(self, path):
    super().__init__(path)
    self.name = self.decodeName()
    self.startPort, self.endPort = self.decodePorts()
    self.zones = self.decodeZones()
    self.hosts = self.decodeHosts()
    return

  def decodeName(self):
    data = self.dataForResource(*ACFG_NAME)
    nameLen = data[0]
    return data[1:1+nameLen].decode("macroman")

  def encodeName(self):
    encName = self.name.encode("macroman")
    return bytes([len(encName)]) + encName

  def decodePorts(self):
    data = self.dataForResource(*ACFG_PORT)
    offset = struct.calcsize(PORT_FORMAT)
    portData = struct.unpack(PORT_FORMAT, data[:offset])
    return portData[2], portData[3]

  def encodePorts(self):
    data = self.dataForResource(*ACFG_PORT)
    offset = struct.calcsize(PORT_FORMAT)
    portData = struct.unpack(PORT_FORMAT, data[:offset])
    encoded = struct.pack(PORT_FORMAT, portData[0], portData[1],
                          self.startPort, self.endPort)
    return encoded + data[offset:]

  def decodeZones(self):
    data = self.dataForResource(*ACFG_ZONE)
    offset = struct.calcsize(ZONE_FORMAT)
    zoneData = struct.unpack(ZONE_FORMAT, data[:offset])
    zones = []
    for idx in range(zoneData[0]):
      nameLen = data[offset]
      zones.append(data[offset+1:offset+1+nameLen].decode("macroman"))
      offset += 1 + nameLen
    return zones

  def encodeZones(self):
    encoded = struct.pack(ZONE_FORMAT, len(self.zones))
    for zone in self.zones:
      encName = zone.encode("macroman")
      encoded += bytes([len(encName)]) + encName
    return encoded

  def decodeHosts(self):
    data = self.dataForResource(*ACFG_HOST)
    offset = struct.calcsize(HOST_FORMAT)
    hostData = struct.unpack(HOST_FORMAT, data[:offset])
    hosts = []
    for idx in range(hostData[1]):
      hostLen = data[offset]
      hosts.append(data[offset+1:offset+1+hostLen].decode("macroman"))
      offset += 1 + hostLen
    return hosts

  def encodeHosts(self):
    data = self.dataForResource(*ACFG_HOST)
    encoded = struct.pack(HOST_FORMAT, data[0], len(self.hosts))
    for host in self.hosts:
      encName = host.encode("macroman")
      encoded += struct.pack(">B", len(encName)) + encName
    return encoded

  def setRouterName(self, name):
    self.name = name
    return

  def setZoneName(self, name):
    self.zones = [name]
    return

  def setZoneNumber(self, start, end):
    self.startPort = start
    self.endPort = end
    return

  def setHosts(self, hosts):
    self.hosts = hosts
    return

  def save(self):
    self.setDataForResource(self.encodeName(), *ACFG_NAME)
    self.setDataForResource(self.encodePorts(), *ACFG_PORT)
    self.setDataForResource(self.encodeZones(), *ACFG_ZONE)
    self.setDataForResource(self.encodeHosts(), *ACFG_HOST)
    super().save()
    return

def build_argparser():
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("file", help="Apple Internet Router config file")
  parser.add_argument("--appletalk_zone", help="name of AppleTalk zone")
  parser.add_argument("--appletalk_number", type=int, help="number of AppleTalk network")
  parser.add_argument("--appletalk_hosts",
                      help="comma separated list of Apple Internet Router hosts")
  return parser

def main():
  args = build_argparser().parse_args()
  airconf = AIRConfig(args.file)

  edited = False
  if args.appletalk_zone:
    airconf.setZoneName(args.appletalk_zone)
    edited = True
  if args.appletalk_number:
    airconf.setZoneNumber(args.appletalk_number, args.appletalk_number)
    edited = True
  if args.appletalk_hosts:
    airconf.setHosts(args.appletalk_hosts.split(","))
    edited = True

  print("Name:", airconf.name)
  print("Ports:", airconf.startPort, airconf.endPort)
  print("Zones:", airconf.zones)
  print("Hosts:", airconf.hosts)

  if edited:
    airconf.save()
  return

if __name__ == '__main__':
  exit(main() or 0)

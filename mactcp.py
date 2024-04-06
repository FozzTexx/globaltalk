#!/usr/bin/env python3
import rsrcdump
import struct
import socket
from dataclasses import dataclass
import os
import argparse

ID_IPLN = 'ipln'
ID_DNSL = 'dnsl'
MACTCP_IP_FORMAT = "> 2I IIII"

@dataclass
class IPInfo:
  ipAddress: str
  mask: str
  gateway: str

@dataclass
class DNSInfo:
  ipAddress: str
  default: bool
  domain: str

class MacTCP:
  def __init__(self, path):
    self.path = path
    self.rsrcPath = path
    self.rsrc = rsrcdump.load(self.rsrcPath)
    self.ipInfo = self.decodeIPInfo()
    self.dns = self.decodeDNS()
    return

  def dataForID(self, dataID):
    return self.rsrc[dataID][128].data

  def decodeIPInfo(self):
    data = self.dataForID(ID_IPLN)
    lenIP = struct.calcsize(MACTCP_IP_FORMAT)
    ipData = struct.unpack(MACTCP_IP_FORMAT, data[:lenIP])
    return IPInfo(
      self.binaryIPToString(ipData[2]),
      self.binaryIPToString(ipData[3]),
      self.binaryIPToString(ipData[5]),
    )

  def encodeIPInfo(self):
    binIP = self.stringIPToBinary(self.ipInfo.ipAddress)
    binMask = self.stringIPToBinary(self.ipInfo.mask)
    binGateway = self.stringIPToBinary(self.ipInfo.gateway)

    data = self.dataForID(ID_IPLN)
    lenIP = struct.calcsize(MACTCP_IP_FORMAT)
    ipData = struct.unpack(MACTCP_IP_FORMAT, data[:lenIP])
    return struct.pack(MACTCP_IP_FORMAT,
                       ipData[0], ipData[1],
                       binIP, binMask, ipData[4], binGateway) + data[lenIP:]

  def decodeDNS(self):
    data = self.dataForID(ID_DNSL)
    numEntries = struct.unpack(">H", data[:2])[0]
    offset = 2
    entries = []
    for idx in range(numEntries):
      dnsData = struct.unpack(">IB", data[offset:offset+5])
      offset += 5
      domainLen = data[offset:].index(0x00)
      entries.append(DNSInfo(
        self.binaryIPToString(dnsData[0]),
        dnsData[1],
        data[offset:offset+domainLen].decode("macroman")
      ))
      offset += domainLen + 1
    return entries

  def encodeDNS(self):
    data = struct.pack(">H", len(self.dns))
    for entry in self.dns:
      entryData = struct.pack(">IB", self.stringIPToBinary(entry.ipAddress), entry.default)
      entryData += entry.domain.encode("macroman")
      entryData += bytes([0x00])
      data += entryData
    return data

  def setIPAddress(self, ipAddress, mask=None, gateway=None):
    if not isinstance(ipAddress, str):
      raise ValueError("Unknown format for ipAddress")

    if '/' in ipAddress:
      ipAddress, mask = ipAddress.split("/")

    if mask and '.' not in mask:
      lenMask = int(mask)
      mask = self.binaryIPToString(((1 << lenMask) - 1) << (32 - lenMask))

    self.ipInfo.ipAddress = ipAddress
    if mask:
      self.ipInfo.mask = mask
    if gateway:
      self.ipInfo.gateway = gateway
    return

  def hasDefaultDNS(self):
    for entry in self.dns:
      if entry.default:
        return True
    return False

  def addDNS(self, server, domain, default=False):
    if not self.hasDefaultDNS() and domain != ".":
      default = True
    self.dns.append(DNSInfo(server, default, domain))
    return

  def save(self):
    self.rsrc[ID_IPLN][128].data = self.encodeIPInfo()
    self.rsrc[ID_DNSL][128].data = self.encodeDNS()

    data = self.rsrc.pack()
    with open(self.path, "wb") as f:
      f.write(data)

    return

  @staticmethod
  def binaryIPToString(binaryIP):
    return socket.inet_ntoa(struct.pack("!L", binaryIP))

  @staticmethod
  def stringIPToBinary(stringIP):
    return struct.unpack("!L", socket.inet_aton(stringIP))[0]

def build_argparser():
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("mactcp", help="MacTCP file")
  parser.add_argument("ip_address", nargs="?", help="IP address to set")
  parser.add_argument("gateway", nargs="?", help="gateway address to set")
  return parser

def main():
  args = build_argparser().parse_args()
  mtcp = MacTCP(args.mactcp)

  edited = False
  if args.ip_address:
    mtcp.setIPAddress(args.ip_address, gateway=args.gateway)
    edited = True

  print(mtcp.ipInfo)
  print(mtcp.dns)

  if edited:
    mtcp.save()
  return

if __name__ == '__main__':
  exit(main() or 0)

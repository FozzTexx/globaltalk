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

import struct
from dataclasses import dataclass, astuple
import crcmod
import os
import argparse

FORMAT_MACBIN = ">B 64p 4s4s B B HHHB B IIIIHB 14s IHBBH"

@dataclass
class MacBinaryHeader:
  version: int
  filename: str
  fileType: bytes
  creator: bytes
  finderFlags1: int
  pad1: int
  windowY: int
  windowX: int
  windowID: int
  protectedFlag: int
  pad2: int
  dataLen: int
  resourceLen: int
  created: int
  modified: int
  commentLen: int
  finderFlags2: int
  pad3: bytes
  fileLen: int
  secondHeaderLen: int
  version2: int
  minVersion: int
  crc: int

class MacBinary:
  def __init__(self, path):
    self.path = path
    hlen = struct.calcsize(FORMAT_MACBIN)
    with open(path, "rb") as f:
      data = f.read(hlen)
    header = struct.unpack(FORMAT_MACBIN, data)
    self.header = MacBinaryHeader(*header)
    return

  def updateDataLength(self, path):
    self.header.dataLen = os.path.getsize(path) if path else 0
    return

  def updateResourceLength(self, path):
    self.header.resourceLen = os.path.getsize(path) if path else 0
    return

  def save(self):
    hlen = struct.calcsize(FORMAT_MACBIN)
    data = struct.pack(FORMAT_MACBIN, *astuple(self.header))

    crc16 = crcmod.predefined.mkPredefinedCrcFun("xmodem")
    self.header.crc = crc16(data[:hlen-2])
    data = data[:hlen-2] + struct.pack(">H", self.header.crc) + bytes([0] * 128)
    data = data[:128]
    with open(self.path, "r+b") as f:
      f.write(data)
    return

def build_argparser():
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("file", help="file to print MacBinary header")
  return parser

def main():
  args = build_argparser().parse_args()
  macbin = MacBinary(args.file)
  print(macbin.header)
  return

if __name__ == '__main__':
  exit(main() or 0)

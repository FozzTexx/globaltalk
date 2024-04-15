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

from .macresource import MacResource

import rsrcdump
import struct
from dataclasses import dataclass
import argparse

PREF_FILE = ('STR ', 1002)
PREF_CNID = ('StID', 1002)
PREF_STRT = ('strt', 1000)

CNID_FORMAT = ">I"
STRT_FORMAT = ">B"

class AIRPrefs(MacResource):
  def __init__(self, path):
    super().__init__(path)
    self.filename = self.decodeFile()
    self.cnid = self.decodeCNID()
    self.autostart = self.decodeAutostart()
    return

  def decodeFile(self):
    data = self.dataForResource(*PREF_FILE)
    nameLen = data[0]
    return data[1:1+nameLen].decode("macroman")

  def encodeFile(self):
    encFile = self.filename.encode("macroman")
    return bytes([len(encFile)]) + encFile

  def decodeCNID(self):
    data = self.dataForResource(*PREF_CNID)
    return struct.unpack(CNID_FORMAT, data)[0]

  def encodeCNID(self):
    return struct.pack(CNID_FORMAT, self.cnid)

  def decodeAutostart(self):
    data = self.dataForResource(*PREF_STRT)
    offset = struct.calcsize(STRT_FORMAT)
    bits = struct.unpack(STRT_FORMAT, data[:offset])[0]
    return bool((bits >> 7) & 1)

  def encodeAutostart(self):
    data = self.dataForResource(*PREF_STRT)
    offset = struct.calcsize(STRT_FORMAT)
    bits = struct.unpack(STRT_FORMAT, data[:offset])[0]
    bits &= 0x7f
    bits |= self.autostart << 7
    encoded = struct.pack(STRT_FORMAT, bits)
    return encoded + data[offset:]

  def setFilename(self, value):
    self.filename = value
    return

  def setCNID(self, value):
    self.cnid = value
    return

  def setAutostart(self, value):
    self.autostart = value
    return

  def save(self):
    self.setDataForResource(self.encodeFile(), *PREF_FILE)
    self.setDataForResource(self.encodeCNID(), *PREF_CNID)
    self.setDataForResource(self.encodeAutostart(), *PREF_STRT)
    super().save()
    return

def build_argparser():
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("prefs", help="Apple Internet Router prefs file")
  parser.add_argument("--config", help="Path to AIR config")
  parser.add_argument("--autostart", action=argparse.BooleanOptionalAction,
                      help="set autostart flag")
  return parser

def main():
  args = build_argparser().parse_args()
  airprefs = AIRPrefs(args.prefs)

  edited = False

  if args.autostart is not None:
    airprefs.setAutostart(args.autostart)
    edited = True

  print("File:", airprefs.filename)
  print("CNID:", airprefs.cnid)
  print("Autostart:", airprefs.autostart)

  if edited:
    airprefs.save()
  return

if __name__ == '__main__':
  exit(main() or 0)

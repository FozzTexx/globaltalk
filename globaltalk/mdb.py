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

from dataclasses import dataclass
import struct

FORMAT_MDB = ">H II HHHHH II H IH B 27s I H III H II 32s H II 3I I 2H2I"

@dataclass
class MDB:
  signature: int
  created: int
  modified: int
  attrFlags: int
  numFiles: int
  volumeBitmap: int
  unknown1: int
  blockCount: int
  blockSize: int
  clumpSize: int
  extentStart: int
  nextCNID: int
  unusedBlocks: int
  labelSize: int
  label: str
  backupDate: int
  backupSequence: int
  writeCount: int
  extentClumpSize: int
  catalogClumpSize: int
  subdirCount: int
  fileCount: int
  dirCount: int
  finderInfo: bytes
  volumeCacheSize: int
  volumeBitmapCacheSize: int
  overflowSize: int
  overflowRecord1: int
  overflowRecord2: int
  overflowRecord3: int
  catalogFileSize: int
  catalogExtentsRecord1start: int
  catalogExtentsRecord1count: int
  catalogExtentsRecord2: int
  catalogExtentsRecord3: int

def loadMDB(data):
  size = struct.calcsize(FORMAT_MDB)
  return MDB(*struct.unpack(FORMAT_MDB, data[:size]))

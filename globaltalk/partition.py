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

FORMAT_PARTITION = ">HH III 32s 32s IIIIIIIIII 16s"

@dataclass
class Partition:
  signature: int
  pad: int
  mapBlockCount: int
  partitionStart: int
  blockCount: int
  partitionName: bytes
  partitionType: bytes
  dataStart: int
  dataCount: int
  status: int
  bootStart: int
  bootSize: int
  bootAddr: int
  bootAddr2: int
  bootEntry: int
  bootEntry2: int
  bootChecksum: int
  processor: bytes

def loadPartition(data):
  size = struct.calcsize(FORMAT_PARTITION)
  return Partition(*struct.unpack(FORMAT_PARTITION, data[:size]))

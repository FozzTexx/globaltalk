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

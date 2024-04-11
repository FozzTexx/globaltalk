from dataclasses import dataclass
import struct

INDEX_NODE = 0
HEADER_NODE = 1
MAP_NODE = 2
LEAF_NODE = 0xff

DIR_RECORD = 1
FILE_RECORD = 2
DIR_THREAD = 3
FILE_THREAD = 4

FORMAT_NODE = ">II BB HH"
FORMAT_KEY = ">I32pI"

@dataclass
class BTreeNode:
  nextNode: int
  prevNode: int
  nodeType: int
  nodeLevel: int
  recordCount: int
  reserved: int
  records: tuple

@dataclass
class IndexEntry:
  parentCNID: int
  name: str
  nodeID: int

@dataclass
class LeafEntry:
  parentCNID: int
  name: str
  data: bytes

FORMAT_DIRREC = ">HH IIII 16s 16s 16s"
  
@dataclass
class DirectoryRecord:
  flags: int
  count: int
  cnid: int
  created: int
  modified: int
  backup: int
  finderInfo: bytes
  extendedInfo: bytes
  reserved: bytes

FORMAT_FILEREC = ">BB 16s I H II H IIIII 16s H 12s 12s I"

@dataclass
class FileRecord:
  flags: int
  fileType: int
  finderInfo: bytes
  cnid: int
  dataBlock: int
  dataSize: int
  dataAllocated: int
  resourceBlock: int
  resourceSize: int
  resourceAllocated: int
  craeted: int
  modified: int
  backup: int
  extendedInfo: bytes
  clumpSize: int
  dataExtents: bytes
  resourceExtents: bytes
  reserved: int

FORMAT_THREADREC = ">8s I 32p"

@dataclass
class ThreadRecord:
  reserved: bytes
  parentCNID: int
  name: bytes
  
def loadBTree(data):
  size = struct.calcsize(FORMAT_NODE)
  bt_data = struct.unpack(FORMAT_NODE, data[:size])
  count = (len(data) - size) // 2
  records = struct.unpack(f">{count}H", data[size:])[::-1]
  btree = BTreeNode(*bt_data, records)
  btree.records = btree.records[:btree.recordCount+1]
  if btree.nodeType == HEADER_NODE:
    btree.records = (loadBTreeHeader(data[records[0]:]),
                     #data[records[1]:records[1]+128],
                     #data[records[2]:records[2]+256],
                     )
  elif btree.nodeType == INDEX_NODE:
    fmtlen = struct.calcsize(FORMAT_KEY)
    btree.records = [IndexEntry(*struct.unpack(FORMAT_KEY, data[x+2:x+2+fmtlen]))
                     if data[x] else None
                     for x in btree.records[:-1]]
  else:
    fmtlen = struct.calcsize(FORMAT_KEY)
    records = []
    for idx in range(len(btree.records) - 1):
      offset = btree.records[idx]
      reclen = data[offset]
      rectotal = btree.records[idx+1] - offset
      if reclen:
        record = struct.unpack(FORMAT_KEY, data[offset+2:offset+2+fmtlen])
        pointer = offset+reclen+1
        pointer = (pointer + 1) // 2 * 2
        rectype = data[pointer]
        recdata = data[pointer:pointer+4]
        if rectype == DIR_RECORD:
          dlen = struct.calcsize(FORMAT_DIRREC)
          pointer += 2
          recdata = DirectoryRecord(*struct.unpack(FORMAT_DIRREC, data[pointer:pointer+dlen]))
        elif rectype == FILE_RECORD:
          dlen = struct.calcsize(FORMAT_FILEREC)
          pointer += 2
          recdata = FileRecord(*struct.unpack(FORMAT_FILEREC, data[pointer:pointer+dlen]))
        elif rectype == DIR_THREAD or rectype == FILE_THREAD:
          dlen = struct.calcsize(FORMAT_THREADREC)
          pointer += 2
          recdata = ThreadRecord(*struct.unpack(FORMAT_THREADREC, data[pointer:pointer+dlen]))
        else:
          raise ValueError("Unhandled rectype", rectype)
        records.append(LeafEntry(*record[:2], recdata))
      else:
        records.append(None)
    btree.records = records
    
  return btree

FORMAT_HEADER = ">H IIII HH II H I BB I"# 64s"

@dataclass
class BTreeHeader:
  depth: int
  rootNode: int
  dataCount: int
  firstLeaf: int
  lastLeaf: int
  nodeSize: int
  keySize: int
  nodeCount: int
  freeCount: int
  reserved1: int
  clumpSize: int
  fileType: int
  keyType: int
  attributes: int
  #reserved2: bytes

def loadBTreeHeader(data):
  size = struct.calcsize(FORMAT_HEADER)
  return BTreeHeader(*struct.unpack(FORMAT_HEADER, data[:size]))

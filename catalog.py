#!/usr/bin/env python3
import argparse
import binascii
import struct

from mdb import loadMDB
from btree import loadBTree, IndexEntry
from macdisk import HFSDisk

MDB_START = 2

class Catalog:
  def __init__(self, diskObj):
    self.disk = diskObj
    self.mdb = loadMDB(self.disk.readSector(MDB_START))

    #print(self.mdb)
    firstBlock = self.disk.readBlock(self.mdb.catalogExtentsRecord1start,
                                     self.mdb.blockSize, self.mdb.extentStart)
    self.btree = loadBTree(firstBlock)
    #print(self.btree)

    self.nodeSize = self.btree.records[0].nodeSize
    self.nodesPerBlock = self.mdb.blockSize // self.nodeSize

    self.rootNodeID = self.btree.records[0].rootNode
    # print("ROOT NODE")
    # print(self.rootNode)

    # print()
    # print("RECURSE")
    # self.recurseChain(self.rootNode)
    return

  def sectorForNode(self, nodeNum):
    sector = self.mdb.extentStart + nodeNum \
      + self.mdb.catalogExtentsRecord1start * self.nodesPerBlock
    return sector
  
  def loadNode(self, nodeNum):
    return loadBTree(self.disk.readSector(self.sectorForNode(nodeNum)))

  def dumpChain(self, leafNum):
    node = self.loadNode(leafNum)
    print(node)
    if node.nextNode:
      self.dumpChain(node.nextNode)
    return

  def recurseChain(self, node, level=0):
    for record in node.records:
      if record is None:
        break
      print("  " * level, record)
      if isinstance(record, IndexEntry):
        self.recurseChain(self.loadNode(record.nodeID), level=level+1)
    return

  def findNode(self, key, nodeID=None):
    if nodeID is None:
      nodeID = self.rootNodeID
    node = self.loadNode(nodeID)
    match = None
    for idx, record in enumerate(node.records):
      recordKey = (record.parentCNID, record.name.decode("macroman"))
      if key == recordKey:
        return nodeID, node, idx, record
      if key < recordKey:
        break
      match = record

    if isinstance(match, IndexEntry):
      return self.findNode(key, match.nodeID)
    return None

def build_argparser():
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("hd", help="HD image to print the catalog of")
  parser.add_argument("cnid", type=int, nargs="?", help="cnid to find")
  parser.add_argument("--flag", action="store_true", help="flag to do something")
  return parser

def hexdump(data):
  split_data = [data[x:x+16] for x in range(0, len(data), 16)]
  for row in split_data:
    ascii = "".join([chr(x) if x >= ord(' ') and x < 127 else '.' for x in row])
    line = binascii.hexlify(row).decode("UTF8")
    print(" ".join([line[x:x+4] for x in range(0, len(line), 4)]), ascii)
  return

def main():
  args = build_argparser().parse_args()

  disk = HFSDisk(args.hd)
  catalog = Catalog(disk)

  if not args.cnid:
    catalog.recurseChain(catalog.loadNode(catalog.rootNodeID))
  else:
    node = catalog.findNode((args.cnid, ""))
    print("Found", node)
    if node is not None:
      hexdump(disk.readSector(catalog.sectorForNode(node[0])))

  return

if __name__ == '__main__':
  exit(main() or 0)
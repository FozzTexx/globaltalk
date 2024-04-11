from partition import loadPartition
import subprocess

SECTOR_SIZE = 512

class HFSDisk:
  def __init__(self, path):
    self.path = path
    self.stream = open(self.path, "r+b")
    self.stream.seek(SECTOR_SIZE, 0)
    partitionMap = loadPartition(self.stream.read(SECTOR_SIZE))
    if partitionMap.signature != 0x504d:
      raise ValueError("Not a valid Apple Partition Map")
    partition = partitionMap
    found = False
    for idx in range(partitionMap.mapBlockCount):
      ptype = partition.partitionType.split(b"\x00", 1)[0].decode("macroman")
      if ptype == "Apple_HFS":
        found = True
        break
      partition = loadPartition(self.stream.read(SECTOR_SIZE))
    if not found:
      raise ValueError("Unable to find HFS partition")
    self.volumeOffset = partition.partitionStart
    return

  def readSector(self, sector):
    offset = (sector + self.volumeOffset) * SECTOR_SIZE
    #print("Reading:", hex(offset))
    self.stream.seek(offset, 0)
    return self.stream.read(SECTOR_SIZE)

  def writeSector(self, sector, data):
    offset = (sector + self.volumeOffset) * SECTOR_SIZE
    #print("Writing:", hex(offset))
    self.stream.seek(offset, 0)
    return self.stream.write(data)

  def readBlock(self, blockNum, blockSize, baseSector):
    base = (baseSector + self.volumeOffset) * SECTOR_SIZE
    offset = (blockNum * blockSize) + base
    #print("Block:", blockNum, hex(offset))
    self.stream.seek(offset, 0)
    return self.stream.read(blockSize)

  def mount(self):
    cmd = ["hmount", self.path]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return

  def unmount(self):
    cmd = ["humount"]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return

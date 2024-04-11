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

import rsrcdump

class MacResource:
  def __init__(self, path):
    self.path = path
    self.rsrc = rsrcdump.load(self.path)
    return

  def dataForResource(self, resourceType, resourceID):
    return self.rsrc[resourceType][resourceID].data

  def setDataForResource(self, data, resourceType, resourceID):
    self.rsrc[resourceType][resourceID].data = data
    return

  def save(self):
    data = self.rsrc.pack()
    with open(self.path, "wb") as f:
      f.write(data)
    return

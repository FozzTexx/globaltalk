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

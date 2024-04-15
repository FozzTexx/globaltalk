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

from .macbinary import MacBinary

import subprocess
import tempfile
import os

class MountFailed(Exception):
  pass

class UnmountFailed(Exception):
  pass

class MacFile:
  def __init__(self, diskPath, macPath, dataPath=None):
    self.diskPath = diskPath
    self.macPath = macPath
    self._dataPath = dataPath
    return

  def load(self):
    self.temp = tempfile.TemporaryDirectory()

    cmd1 = ["hcopy", "-m", self.macPath, "-"]
    cmd2 = ["macunpack", "-f"]

    if self._dataPath:
      with open(self._dataPath, "rb") as f:
        proc2 = subprocess.Popen(cmd2, stdin=f, cwd=self.temp.name)
        proc2.wait()
    else:
      self.mount()
      proc1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
      proc2 = subprocess.Popen(cmd2, stdin=proc1.stdout, cwd=self.temp.name)
      proc2.wait()
      self.unmount()

    return

  def save(self):
    header = MacBinary(self.infoPath)
    header.updateDataLength(self.dataPath)
    header.updateResourceLength(self.resourcePath)
    header.save()

    parts = [os.path.join(self.temp.name, x) for x in os.listdir(self.temp.name)
             if x.endswith((".data", ".rsrc", ".info"))]
    cmd1 = ["macstream", *parts]
    cmd2 = ["hcopy", "-m", "-", self.macPath]

    self.mount()
    proc1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
    proc2 = subprocess.Popen(cmd2, stdin=proc1.stdout, cwd=self.temp.name)
    proc2.wait()
    self.unmount()
    return

  def mount(self):
    cmd = ["hmount", self.diskPath]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return

  def unmount(self):
    cmd = ["humount"]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return

  def fileWithExtension(self, extension):
    if not hasattr(self, 'temp'):
      self.load()
    for f in os.listdir(self.temp.name):
      if f.endswith(extension):
        return os.path.join(self.temp.name, f)
    return None

  @property
  def infoPath(self):
    return self.fileWithExtension(".info")

  @property
  def dataPath(self):
    return self.fileWithExtension(".data")

  @property
  def resourcePath(self):
    return self.fileWithExtension(".rsrc")

  @property
  def catalogID(self):
    self.mount()
    cmd = ["hls", "-id", self.macPath]
    p = subprocess.run(cmd, capture_output=True, text=True)
    self.unmount()
    cnid = int(p.stdout.strip().split()[0])
    return cnid

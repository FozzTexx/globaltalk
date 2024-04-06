import subprocess
import tempfile
import os

from macbinary import MacBinary

class MountFailed(Exception):
  pass

class UnmountFailed(Exception):
  pass

class MacFile:
  def __init__(self, diskPath, macPath, dataPath=None):
    self.diskPath = diskPath
    self.macPath = macPath
    self.temp = tempfile.TemporaryDirectory()

    cmd1 = ["hcopy", "-m", self.macPath, "-"]
    cmd2 = ["macunpack", "-f"]

    if dataPath:
      with open(dataPath, "rb") as f:
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

import subprocess
import tempfile
import os

class MountFailed(Exception):
  pass

class UnmountFailed(Exception):
  pass

class MacFile:
  def __init__(self, diskPath, macPath):
    self.diskPath = diskPath
    self.macPath = macPath

    cmd1 = ["hcopy", "-m", self.macPath, "-"]
    cmd2 = ["macunpack", "-f"]

    self.mount()
    self.temp = tempfile.TemporaryDirectory()
    proc1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
    proc2 = subprocess.Popen(cmd2, stdin=proc1.stdout, cwd=self.temp.name)
    self.unmount()

    return

  def save(self):
    parts = [x for x in os.listdir(self.temp.name) if x.endswith((".data", ".rsrc", ".info"))]
    cmd1 = ["macstream", *parts]
    cmd2 = ["hcopy", "-m", "-", self.macPath]

    self.mount()
    proc1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
    proc2 = subprocess.Popen(cmd2, stdin=proc1.stdout, cwd=self.temp.name)
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

  @property
  def resourcePath(self):
    for f in os.listdir(self.temp.name):
      if f.endswith(".rsrc"):
        return f
    return None

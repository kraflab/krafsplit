# store doom time (converted from raw tic count)
class dTime:
  m = 0
  s = 0
  c = 0
  
  def __init__(self, other=None, text=None):
    if other is None and text is None:
      self.m = 0
      self.s = 0
      self.c = 0
    elif text is None:
      self.copy(other)
    else:
      sub = text.split(":")
      self.m = int(sub[0])
      sub = sub[1].split(".")
      self.s = int(sub[0])
      self.c = int(sub[1])
  
  def zero(self):
    self.m = 0
    self.s = 0
    self.c = 0
  
  def exists(self):
    return self.m > 0 or self.s > 0 or self.c > 0
  
  def copy(self, other):
    self.m = other.m
    self.s = other.s
    self.c = other.c
  
  def betterThan(self, other):
    if not other.exists():
      return True
    if self.m > other.m:
      return False
    elif self.m < other.m:
      return True
    if self.s > other.s:
      return False
    elif self.s < other.s:
      return True
    if self.c > other.c:
      return False
    elif self.c < other.c:
      return True
    return False
  
  def compareSecs(self, other):
    if not other.exists():
      return 0
    if self.m > other.m:
      return -1
    elif self.m < other.m:
      return 1
    if self.s > other.s:
      return -1
    elif self.s < other.s:
      return 1
    return 0
  
  def deltaSecs(self,other):
    return (self.m - other.m) * 60 + (self.s - other.s)
  
  def addSecs(self, t):
    self.s += t.s
    self.m += t.m
    m = int(self.s / 60)
    self.s -= m * 60
    self.m += m
    if self.c > 0 or t.c > 0:
      self.c = 1
    else:
      self.c = 0
  
  def add(self, t):
    self.c += t.c
    self.s += t.s
    s = int(self.c / 100)
    self.c -= s * 100
    self.s += s
    self.m += t.m
    m = int(self.s / 60)
    self.s -= m * 60
    self.m += m
  
  def fromTics(self, t):
    self.s = int(t / 35)
    self.c = int(100.0 * (t - self.s * 35) / 35 + 0.5)
    self.m = int(self.s / 60)
    self.s = self.s - self.m * 60
  
  def toString(self, centi=True, forceM=False):
    s = str(self.s)
    if (self.m > 0 or forceM) and len(s) == 1:
      s = "0" + s
    m = str(self.m)
    c = str(self.c)
    if len(c) == 1:
      c = "0" + c
    val = ""
    if (self.m == 0 and not forceM):
      val = s
    else:
      val = m + ":" + s
    if centi:
      val += "." + c
    return val
  
  def toSimpleString(self):
    return "{}:{}.{}".format(self.m, self.s, self.c)

# doom time (converted from raw tic count)
class dTime:
    m = 0
    s = 0
    c = 0
    
    # if other is supplied, copy
    # if a time string is supplied, convert into dTime object
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
    
    # return true if this time is faster than other
    def better_than(self, other):
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
    
    # return -1 if other time is shorter, 1 if longer (ignoring tics)
    def compare_secs(self, other):
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
    
    # difference between time, in seconds
    def delta_secs(self,other):
        return (self.m - other.m) * 60 + (self.s - other.s)
    
    # add times, ignoring tics
    def add_secs(self, t):
        self.s += t.s
        self.m += t.m
        m = int(self.s / 60)
        self.s -= m * 60
        self.m += m
        if self.c > 0 or t.c > 0:
            self.c = 1
        else:
            self.c = 0
    
    # add times, including tics
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
    
    # convert tic count into full time
    def from_tics(self, t):
        self.s = int(t / 35)
        self.c = int(100.0 * (t - self.s * 35) / 35 + 0.5)
        self.m = int(self.s / 60)
        self.s = self.s - self.m * 60
    
    # nice looking string for display
    def to_string(self, centi=True, forceM=False):
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
    
    # simple string for splits file
    def to_simple_string(self):
        return "{}:{}.{}".format(self.m, self.s, self.c)

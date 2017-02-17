import ctypes
import win32api

memory  = ctypes.windll.kernel32.ReadProcessMemory
buffer  = ctypes.create_string_buffer(4)
port    = None
portPid = 0
newPid  = 0

# memory addresses (prboom+ 2.5.1.4-stable)
MONSTER_ALIVE = 0x005DB184
MONSTER_TOTAL = 0x005DB388
KILL_COUNT    = 0x005820AC
SECRET_TOTAL  = 0x005DB390
SECRET_FOUND  = 0x005820B4
ITEM_FOUND    = 0x005820B0
ITEM_TOTAL    = 0x005DB394
TICS          = 0x005DB164
MAP_NUMBER    = 0x005DAEE4
INTERMISSION  = 0x005DB33C
RECORDING     = 0x005DB07C

# storage of memory extraction
monsterAlive = 0
monsterTotal = 0
killCount    = 0
secretTotal  = 0
secretFound  = 0
itemFound    = 0
itemTotal    = 0
tics         = 0
mapNumber    = 0
intermission = 0
recording    = 0

# converts string of memory bytes to value, probably
# a function in standard but i was too lazy to look
def convert(buff, n, signed=False):
  val = 0
  for i in range(0, n):
    val += ord(buff[i]) << (i * 8)
  if signed and val > (2 ** (i * 8)) / 2:
    val -= 2 ** (i * 8)
  return val

def readFail():
  global port, recording
  port = None
  recording = False

# not sure on all the sizes, but these have worked
# will change if anything weird occurs
def parseMemory(Screen):
  global monsterAlive, monsterTotal, killCount, secretTotal, secretFound
  global itemFound, itemTotal, tics, mapNumber, intermission
  global portPid, port, recording
  
  if newPid != portPid:
    portPid = newPid
    # 0x010 is read
    Screen.resetSplits()
    port = win32api.OpenProcess(0x010, False, portPid)
  
  if port is None:
    return

  if memory(port.handle, MONSTER_ALIVE, buffer, 2, 0) == 0:
    return readFail()
  monsterAlive = convert(buffer, 2)
  
  if memory(port.handle, MONSTER_TOTAL, buffer, 2, 0) == 0:
    return readFail()
  monsterTotal = convert(buffer, 2)
  
  if memory(port.handle, KILL_COUNT, buffer, 2, 0) == 0:
    return readFail()
  killCount = convert(buffer, 2)
  
  if memory(port.handle, SECRET_TOTAL, buffer, 2, 0) == 0:
    return readFail()
  secretTotal = convert(buffer, 2)
  
  if memory(port.handle, SECRET_FOUND, buffer, 2, 0) == 0:
    return readFail()
  secretFound = convert(buffer, 2)
  
  if memory(port.handle, ITEM_FOUND, buffer, 2, 0) == 0:
    return readFail()
  itemFound = convert(buffer, 2)
  
  if memory(port.handle, ITEM_TOTAL, buffer, 2, 0) == 0:
    return readFail()
  itemTotal = convert(buffer, 2)
  
  if memory(port.handle, TICS, buffer, 2, 0) == 0:
    return readFail()
  tics = convert(buffer, 2)
  
  if memory(port.handle, MAP_NUMBER, buffer, 1, 0) == 0:
    return readFail()
  mapNumber = convert(buffer, 1)
  
  if memory(port.handle, INTERMISSION, buffer, 1, 0) == 0:
    return readFail()
  intermission = convert(buffer, 1)
  
  if memory(port.handle, RECORDING, buffer, 1, 0) == 0:
    return readFail()
  recording = convert(buffer, 1)

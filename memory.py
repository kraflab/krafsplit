import ctypes
import win32api

# alias for windows memory read
memory = ctypes.windll.kernel32.ReadProcessMemory
buffer = ctypes.create_string_buffer(4)

# port is the process returned from the file system
port = None
port_pid = 0 # active port process id
new_pid  = 0 # newly detected port process id

# memory addresses (prboom+ 2.5.1.4-stable)
MONSTERS_ALIVE = 0x005DB184
MONSTER_TOTAL = 0x005DB388
KILL_COUNT    = 0x005820AC
SECRET_TOTAL  = 0x005DB390
SECRETS_FOUND  = 0x005820B4
ITEMS_FOUND    = 0x005820B0
ITEM_TOTAL    = 0x005DB394
TICS          = 0x005DB164
MAP_NUMBER    = 0x005DAEE4
INTERMISSION  = 0x005DB33C
RECORDING     = 0x005DB07C

# storage of memory extraction
monsters_alive = 0
monster_total  = 0
kill_count     = 0
secret_total   = 0
secrets_found  = 0
items_found    = 0
item_total     = 0
tics           = 0
map_number     = 0
intermission   = 0
recording      = 0

# converts string of memory bytes to value, probably
# a function in standard but i was too lazy to look
def convert(buff, n, signed=False):
    val = 0
    for i in range(0, n):
        val += ord(buff[i]) << (i * 8)
    if signed and val > (2 ** (i * 8)) / 2:
        val -= 2 ** (i * 8)
    return val

# tasks to be performed if parse_memory has a read error
def read_fail():
    global port, recording
    port = None
    recording = False

# not sure on all the sizes, but these have worked
# will change if anything weird occurs
def parse_memory(screen):
    global monsters_alive, monster_total, kill_count, secret_total, secrets_found
    global items_found, item_total, tics, map_number, intermission
    global port_pid, port, recording
    
    # get new process handle if the process has changed
    if new_pid != port_pid:
        port_pid = new_pid
        # 0x010 is read
        screen.reset_splits()
        port = win32api.OpenProcess(0x010, False, port_pid)
    
    # exit if no process
    if port is None:
        return
    
    # read each memory address and convert to python type
    if memory(port.handle, MONSTERS_ALIVE, buffer, 2, 0) == 0:
        return read_fail()
    monsters_alive = convert(buffer, 2)
  
    if memory(port.handle, MONSTER_TOTAL, buffer, 2, 0) == 0:
        return read_fail()
    monster_total = convert(buffer, 2)
    
    if memory(port.handle, KILL_COUNT, buffer, 2, 0) == 0:
        return read_fail()
    kill_count = convert(buffer, 2)
    
    if memory(port.handle, SECRET_TOTAL, buffer, 2, 0) == 0:
        return read_fail()
    secret_total = convert(buffer, 2)
    
    if memory(port.handle, SECRETS_FOUND, buffer, 2, 0) == 0:
        return read_fail()
    secrets_found = convert(buffer, 2)
    
    if memory(port.handle, ITEMS_FOUND, buffer, 2, 0) == 0:
        return read_fail()
    items_found = convert(buffer, 2)
    
    if memory(port.handle, ITEM_TOTAL, buffer, 2, 0) == 0:
        return read_fail()
    item_total = convert(buffer, 2)
    
    if memory(port.handle, TICS, buffer, 2, 0) == 0:
        return read_fail()
    tics = convert(buffer, 2)
    
    if memory(port.handle, MAP_NUMBER, buffer, 1, 0) == 0:
        return read_fail()
    map_number = convert(buffer, 1)
    
    if memory(port.handle, INTERMISSION, buffer, 1, 0) == 0:
        return read_fail()
    intermission = convert(buffer, 1)
    
    if memory(port.handle, RECORDING, buffer, 1, 0) == 0:
        return read_fail()
    recording = convert(buffer, 1)

## KrafSplit
This is an autosplitter / autotimer for doom demo recording.  It automates the
timing by locating and reading the source port's memory.  It knows when you are
recording, so you do not need to mess with the splits if you need to boot up a
map to test something.  The memory addresses in here are for prboom+ v2.5.1.4,
so in order to use a different version (or port) you will need to determine the
relevant addresses and substitute them.  
  
The user interface isn't the best right now, but it does the job, and it works.
Currently the program is windows-only because I used the win32api for memory
access, but I'm sure an equivalent library could be used to port the code.

### Basic Usage
O: Open splits  
C: Close splits  
S: Save splits  
T: Set splits title  
Y: Set splits subtitle (e.g., UV Speed)  
H: Toggle split hiding  
N: Set the number of splits  
  
To set custom names for the splits or edit other details, open the splits file
in a text editor and set things there.

#### Contributors
Written by Kraflab

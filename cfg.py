import os
import pyglet
label = pyglet.text.Label

# color constants
WHITE        = (255, 255, 255, 255)
BLACK        = (  0,   0,   0, 255)
GRAY         = (128, 128, 128, 255)

LIGHTGRAY    = (192, 192, 192, 255)
RED          = (255,   0,   0, 255)
GREEN        = (  0, 255,   0, 255)
BLUE         = (  0,   0, 255, 255)

YELLOW       = (255, 255,   0, 255)
TEAL         = (  0, 255, 255, 255)
MAGENTA      = (255,   0, 255, 255)

LIGHTRED     = (255, 128, 128, 255)
LIGHTGREEN   = (128, 255, 128, 255)
LIGHTBLUE    = (128, 128, 255, 255)
LIGHTYELLOW  = (255, 255, 128, 255)
LIGHTTEAL    = (128, 255, 255, 255)
LIGHTMAGENTA = (255, 128, 255, 255)

SKYBLUE      = (128, 192, 255, 255)
LAVENDER     = (192, 128, 255, 255)
LIME         = (192, 255, 128, 255)
SEAGREEN     = (128, 255, 192, 255)
PINK         = (255, 128, 192, 255)
PEACH        = (255, 192, 128, 255)

GOLDENROD    = (255, 192,   0, 255)
HOTPINK      = (255,   0, 192, 255)
SEAGREEN2    = (  0, 255, 192, 255)
GREENYELLOW  = (192, 255,   0, 255)
PURPLE       = (192,   0, 255, 255)
SKYBLUE2     = (  0, 192, 255, 255)

exe = "prboom-plus.exe"
lastFile = ""
hideSplits = 0
WindowWidth   = 320
WindowHeight  = 720
BigFontSize   = 32
FontSize      = 24
SmallFontSize = 20
titlePadding  = 16
XPadding      = 16
YPadding      = 16
timeBadColor     = PINK
timeBestColor    = SKYBLUE
timeGoodColor    = LIME
timeNeutralColor = LIGHTYELLOW
titleColor       = WHITE
subTitleColor    = LIGHTGRAY
splitNameColor   = WHITE
completionColor  = WHITE
attemptsColor    = LIGHTBLUE
resetsColor      = LIGHTBLUE
fontName = 'Maiden Orange'
fontFile = 'resource/maiden-orange/MaidenOrange.ttf'

def getCharacterSize(fontSize):
  l = label("0", font_name=fontName, font_size=fontSize)
  return l.content_width, l.content_height

def init():
  global BigCharacterX, BigCharacterY
  global CharacterX, CharacterY
  global SmallCharacterX, SmallCharacterY
  
  pyglet.font.add_file(fontFile)
  pyglet.font.load(fontName)
  BigCharacterX, BigCharacterY     = getCharacterSize(BigFontSize)
  CharacterX, CharacterY           = getCharacterSize(FontSize)
  SmallCharacterX, SmallCharacterY = getCharacterSize(SmallFontSize)

def readConfig(window, screen):
  global lastFile, titlePadding, hideSplits
  if not os.path.isfile("config.txt"):
    return
  f = open("config.txt", 'r')
  
  x, y = window.get_location()
  for line in f:
    l = line.rstrip().split(" ")
    if len(l) == 3:
      option = l[0]
      if option == "last_file":
        screen.readSplits(l[2])
        lastFile = l[2]
      elif option == "window_x":
        window.set_location(int(l[2]), y)
        x, y = window.get_location()
      elif option == "window_y":
        window.set_location(x, int(l[2]))
        x, y = window.get_location()
      elif option == "title_padding":
        titlePadding = int(l[2])
      elif option == "hide_splits":
        hideSplits = int(l[2])
  
  f.close()

def saveConfig(window):
  f = open("config.txt", 'w')
  
  x, y = window.get_location()
  print("last_file = " + lastFile, file=f)
  print("window_x = " + str(x), file=f)
  print("window_y = " + str(y), file=f)
  print("title_padding = " + str(titlePadding), file=f)
  print("hide_splits = " + str(hideSplits), file=f)
  
  f.close()

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

# default configurations
exe = "prboom-plus.exe"
last_file = ""
hide_splits = 0
window_width    = 320
window_height   = 720
big_font_size   = 32
font_size       = 24
small_font_size = 20
title_padding   = 16
x_padding       = 16
y_padding       = 16
time_bad_color     = PINK
time_best_color    = SKYBLUE
time_good_color    = LIME
time_neutral_color = LIGHTYELLOW
title_color        = WHITE
subtitle_color     = LIGHTGRAY
split_name_color   = WHITE
completion_color    = WHITE
attempts_color     = LIGHTBLUE
resets_color       = LIGHTBLUE
font_name = 'Maiden Orange'
font_file = 'resource/maiden-orange/MaidenOrange.ttf'

# determine character width / height for font / size
def get_character_size(font_size):
    l = label("0", font_name=font_name, font_size=font_size)
    return l.content_width, l.content_height

# set up pyglet font and determine character sizes
def init():
    global big_character_x, big_character_y
    global character_x, character_y
    global small_character_x, small_character_y

    pyglet.font.add_file(font_file)
    pyglet.font.load(font_name)
    big_character_x, big_character_y     = get_character_size(big_font_size)
    character_x, character_y             = get_character_size(font_size)
    small_character_x, small_character_y = get_character_size(small_font_size)

# parse configuration file
def read_config(window, screen):
    global last_file, title_padding, hide_splits
    if not os.path.isfile("config.txt"):
        return
    f = open("config.txt", 'r')
    
    x, y = window.get_location()
    for line in f:
        l = line.rstrip().split(" ")
    if len(l) == 3:
        option = l[0]
        if option == "last_file":
            screen.readsplits(l[2])
            last_file = l[2]
        elif option == "window_x":
            window.set_location(int(l[2]), y)
            x, y = window.get_location()
        elif option == "window_y":
            window.set_location(x, int(l[2]))
            x, y = window.get_location()
        elif option == "title_padding":
            title_padding = int(l[2])
        elif option == "hide_splits":
            hide_splits = int(l[2])
  
    f.close()

def save_config(window):
    f = open("config.txt", 'w')
    
    x, y = window.get_location()
    print("last_file = " + last_file, file=f)
    print("window_x = " + str(x), file=f)
    print("window_y = " + str(y), file=f)
    print("title_padding = " + str(title_padding), file=f)
    print("hide_splits = " + str(hide_splits), file=f)
    
    f.close()

import os
import subprocess
import threading
import time
import collections
import ctypes
import win32api
import pyglet
import pyglet.window.key as pykey
import tkinter
from tkinter import filedialog
from tkinter import simpledialog

# call tk to make file dialogs available
root = tkinter.Tk()
root.withdraw()

# improves pyglet performance (allegedly)
pyglet.options['debug_gl'] = False
label = pyglet.text.Label

# might use for tracking sr40 / sr50 inputs later
#def keyHitGlobal(key):
#  return win32api.GetAsyncKeyState(ord(key)) != 0

import key
from dtime import dTime
import memory as mem
from split import Split
import cfg

# set up configuration variables and pyglet
cfg.init()
window = pyglet.window.Window(width=cfg.window_width, height=cfg.window_height, caption='krafSplit')

# container for the splits
class SplitContainer:
    # batches improve draw performance
    label_batch = pyglet.graphics.Batch()
    current_time = dTime()
    total_time   = dTime()
    prev_total   = dTime()
    sum_of_best  = dTime()
    accrued_time = dTime()
    prev_accrued = dTime()
    done_intermission = 0
    attempts    = 0
    maps_played = 0
    current_map = 0
    title     = ""
    subtitle = ""
    splits = []
    total_time_label   = label()
    current_time_label = label()
    best_time_label    = label()
    accrued_time_label = label()
    title_label        = label()
    subtitle_label    = label()
    completion_label   = label()
    reset_label        = label()
    sum_of_best_label  = label()
  
    def __init__(self):
        self.label_batch = pyglet.graphics.Batch()
        self.current_time = dTime()
        self.total_time   = dTime()
        self.prev_total   = dTime()
        self.sum_of_best  = dTime()
        self.prev_accrued = dTime()
        self.accrued_time = dTime()
        self.title = "Untitled"
        self.title_label        = label(self.title,     font_name=cfg.font_name, font_size=cfg.font_size,       x=cfg.x_padding,                    y=cfg.window_height - cfg.y_padding,                  anchor_x='left',  anchor_y='top',    color=cfg.title_color,        batch=self.label_batch)
        self.attempts_label     = label("0",            font_name=cfg.font_name, font_size=cfg.font_size,       x=cfg.window_width - cfg.x_padding, y=self.title_label.y,                                 anchor_x='right', anchor_y='top',    color=cfg.attempts_color,     batch=self.label_batch)
        self.subtitle_label    = label(self.subtitle, font_name=cfg.font_name, font_size=cfg.small_font_size, x=cfg.x_padding,                    y=self.title_label.y - cfg.character_y,               anchor_x='left',  anchor_y='top',    color=cfg.subtitle_color,    batch=self.label_batch)
        self.total_time_label   = label("0:00",         font_name=cfg.font_name, font_size=cfg.big_font_size,   x=cfg.window_width - cfg.x_padding, y=self.subtitle_label.y - cfg.small_character_y,     anchor_x='right', anchor_y='top',    color=cfg.time_neutral_color, batch=self.label_batch)
        self.sum_of_best_label  = label("",             font_name=cfg.font_name, font_size=cfg.big_font_size,   x=cfg.x_padding,                    y=self.subtitle_label.y - cfg.small_character_y,     anchor_x='left',  anchor_y='top',    color=cfg.time_best_color,    batch=self.label_batch)
        self.best_time_label    = label("",             font_name=cfg.font_name, font_size=cfg.small_font_size, x=cfg.x_padding,                    y=self.sum_of_best_label.y - cfg.big_character_y,     anchor_x='left',  anchor_y='top',    color=cfg.time_best_color,    batch=self.label_batch)
        self.current_time_label = label("0.00",         font_name=cfg.font_name, font_size=cfg.small_font_size, x=cfg.window_width - cfg.x_padding, y=self.total_time_label.y - cfg.big_character_y,      anchor_x='right', anchor_y='top',    color=cfg.time_neutral_color, batch=self.label_batch)
        self.reset_label        = label("",             font_name=cfg.font_name, font_size=cfg.small_font_size, x=cfg.window_width - cfg.x_padding, y=self.current_time_label.y - cfg.small_character_y,  anchor_x='right', anchor_y='top',    color=cfg.resets_color,       batch=self.label_batch)
        self.completion_label   = label("",             font_name=cfg.font_name, font_size=cfg.small_font_size, x=cfg.window_width - cfg.x_padding, y=self.reset_label.y - cfg.small_character_y,         anchor_x='right', anchor_y='top',    color=cfg.completion_color,    batch=self.label_batch)
        self.accrued_time_label = label("0:00",         font_name=cfg.font_name, font_size=cfg.small_font_size, x=cfg.x_padding,                    y=cfg.y_padding,                                      anchor_x='left',  anchor_y='bottom', color=cfg.time_neutral_color, batch=self.label_batch)
        self.splits = []
        self.done_intermission = 0
        self.attempts = 0
        self.maps_played = 0
        self.current_map = 0
  
  # set label text and color based on split times
    def update_labels(self):
        self.attempts_label.text = str(self.attempts)
        if self.maps_played == 0:
            self.total_time_label.color = cfg.time_neutral_color
            self.best_time_label.text = ""
            self.reset_label.text = ""
        else:
            if len(self.splits) >= self.maps_played:
                self.best_time_label.text = self.splits[self.maps_played - 1].best_time.to_string()
                if self.best_time_label.text == "0.00":
                    self.best_time_label.text = "---"
                self.reset_label.text = self.splits[self.maps_played - 1].resetText()
            if len(self.splits) < self.maps_played:
                better = 0
            else:
                better = self.total_time.compare_secs(self.splits[self.maps_played - 1].prev_total)
            if better < 0:
                self.total_time_label.color = cfg.time_bad_color
            elif better > 0:
                self.total_time_label.color = cfg.time_good_color
            else:
                self.total_time_label.color = cfg.time_neutral_color
        if self.maps_played == 0:
            self.current_time_label.color = cfg.time_neutral_color
        else:
            if len(self.splits) < self.maps_played:
                better = 0
            else:
                better = self.current_time.compare_secs(self.splits[self.maps_played - 1].prev_time)
            if better < 0:
                self.current_time_label.color = cfg.time_bad_color
            elif better > 0:
                self.current_time_label.color = cfg.time_good_color
            else:
                self.current_time_label.color = cfg.time_neutral_color
        self.total_time_label.text   = self.total_time.to_string(centi=False, forceM=True)
        self.current_time_label.text = self.current_time.to_string()
        self.accrued_time_label.text = self.accrued_time.to_string(centi=True, forceM=True)
    
    # switch the title and update labels
    def update_title(self, new_title="DooM"):
        self.title = new_title
        self.title_label.text = self.title
        self.build_splits()
    
    # switch sub
    def update_subtitle(self, new_title=""):
        self.subtitle = new_title
        self.subtitle_label.text = self.subtitle
        self.build_splits()
    
    # save the splits into a file
    def save_splits_(self, file_name, change_name=True):
        if change_name:
            cfg.last_file = file_name
        
        f = open(file_name, 'w')
        
        print(self.title, file=f)
        print(self.subtitle, file=f)
        print(self.attempts, file=f)
        print(self.accrued_time.to_simple_string(), file=f)
        
        for s in self.splits:
            print(s.name + "; " + s.prev_time.to_simple_string() + " " + s.best_time.to_simple_string() + " " + str(s.resets) + " " + str(s.arrivals), file=f)
        
        f.close()
    
    # wrapper of save function, backs up and queries for path
    def save_splits(self):
        if cfg.last_file != "":
            self.backup("_s")
            self.save_splits_(cfg.last_file)
        else:
            save_path = filedialog.asksaveasfilename(defaultextension=".ks", filetypes=[('krafSplit files', '.ks')])
            if save_path == "":
                return
            self.save_splits_(save_path)
    
    # save the splits into a backup file
    def backup(self, c="_"):
        if cfg.last_file != "":
            self.save_splits_(cfg.last_file + c, change_name=False)
    
    # read splits from file
    def read_splits(self, file_name):
        if not os.path.isfile(file_name):
            return
        self.accrued_time.zero()
        self.splits.clear()
        cfg.last_file = file_name
        f = open(file_name, 'r')
        self.update_title(f.readline().rstrip())
        self.update_subtitle(f.readline().rstrip())
        self.attempts = int(f.readline().rstrip())
        self.prev_accrued = dTime(text=f.readline().rstrip())
        self.accrued_time.copy(self.prev_accrued)
        for line in f:
            l = line.rstrip()
            if len(self.splits) > 0:
                self.splits.append(Split(l, sum=self.splits[-1].prev_total))
            else:
                self.splits.append(Split(l))
        self.build_splits()
        self.backup()
    
    # end the run and overwrite the splits
    def finish_run(self):
        if self.splits[-1].improved():
            for s in self.splits:
                s.overwrite()
    
    # calculate the sum of best times
    def make_sum_of_best(self):
        self.sum_of_best.zero()
        for s in self.splits:
            if not s.best_time.exists():
                self.sum_of_best.zero()
                break
            self.sum_of_best.add_secs(s.best_time)
        self.sum_of_best_label.text = self.sum_of_best.to_string(centi=False, forceM=True)
    
    def update(self):
        # close / reset the splits
        if key.hit(pykey.C):
            self.accrued_time.zero()
            self.prev_accrued.zero()
            self.splits = []
            self.attempts = 0
            self.update_subtitle()
            self.update_title()
            self.build_splits()
            cfg.last_file = ""
        
        # save the splits
        if key.hit(pykey.S):
            self.save_splits()
        
        # set a new title
        if key.hit(pykey.T):
            title = simpledialog.askstring("", "Title")
            if title == "" or title == None:
                title = "Untitled"
            self.update_title(title)
        
        # set a new sub title
        if key.hit(pykey.Y):
            subtitle = simpledialog.askstring("", "Sub Title")
            if subtitle == None:
                subtitle = ""
            self.update_subtitle(subtitle)
        
        # hide or unhide the splits
        if key.hit(pykey.H):
            cfg.hide_splits = int(cfg.hide_splits == 0)
            self.build_splits()
        
        # query to open a new split file
        if key.hit(pykey.O):
            openPath = filedialog.askopenfilename(defaultextension=".ks")
            if openPath != "":
                self.read_splits(openPath)
        
        # change the number of splits
        if key.hit(pykey.N):
            n = simpledialog.askstring("", "Split Count")
            if n is not None:
                n = int(n)
            else:
                n = 0
            while len(self.splits) < n:
                self.splits.append(Split(new=True))
            if n == 0:
                self.splits = []
            else:
                self.splits = self.splits[:n]
            cfg.last_file = ""
            self.build_splits()
        
        # enter here only if a demo is being recorded
        if mem.recording == 1 and mem.port is not None:
            if mem.intermission == 1 and self.done_intermission == 0:
                self.current_time.from_tics(mem.tics)
                self.total_time.copy(self.current_time)
                self.total_time.add_secs(self.prev_total)
                self.done_intermission = 1
                if self.maps_played <= len(self.splits):
                  self.splits[self.maps_played - 1].end(self)
                if self.maps_played == len(self.splits):
                  self.finish_run()
                self.make_sum_of_best()
            elif mem.intermission == 0:
                self.done_intermission = 0
            if self.current_map != mem.map_number:
                self.maps_played += 1
                if len(self.splits) >= self.maps_played:
                  self.splits[self.maps_played - 1].arrivals += 1
                if self.maps_played == 1:
                  self.attempts += 1
                self.current_map = mem.map_number
                self.done_intermission = 0
                self.prev_total.copy(self.total_time)
                self.prev_accrued.copy(self.accrued_time)
            self.current_time.from_tics(mem.tics)
            self.total_time.copy(self.current_time)
            self.total_time.add_secs(self.prev_total)
            self.accrued_time.copy(self.prev_accrued)
            self.accrued_time.add(self.current_time)
            
            # advanced-hud style notes for completion
            if mem.monsters_alive == 0:
                self.completion_label.text = "K"
            elif mem.kill_count == mem.monster_total:
                self.completion_label.text = "k"
            else:
                self.completion_label.text = ""
            if mem.items_found == mem.item_total:
                self.completion_label.text += "I"
            else:
                self.completion_label.text += ""
            if mem.secrets_found == mem.secret_total:
                self.completion_label.text += "S"
            else:
                self.completion_label.text += ""
            
            self.update_labels()
    
    # reset the timer and splits
    def reset_splits(self):
        if len(self.splits) >= self.maps_played and self.maps_played > 0:
            if not self.splits[self.maps_played - 1].ended or len(self.splits) > self.maps_played:
                self.splits[self.maps_played - 1].resets += 1
        mem.recording = 0
        self.maps_played = 0
        mem.map_number = 0
        self.current_map = 0
        mem.tics = 0
        self.total_time.zero()
        self.prev_total.zero()
        self.current_time.zero()
        self.completion_label.text = ""
        self.prev_accrued.copy(self.accrued_time)
        self.update_labels()
    
        for s in self.splits:
            s.reset()
        self.build_splits()
    
    # set up label text and locations
    def build_splits(self):
        subtitle_adjust = cfg.small_character_y
        if self.subtitle == "":
            subtitle_adjust = 0
        
        n = len(self.splits)
        i = 0
        for s in self.splits:
            s.build(self.title_label.y - subtitle_adjust - (i + 1) * cfg.character_y)
            i += 1
        if cfg.hide_splits:
            n = 0
        
        self.make_sum_of_best()
        self.total_time_label.y = self.title_label.y - subtitle_adjust - cfg.character_y * (n + 1)
        self.current_time_label.y = self.total_time_label.y - cfg.big_character_y
        self.sum_of_best_label.y = self.total_time_label.y
        self.best_time_label.y = self.current_time_label.y
        self.reset_label.y = self.current_time_label.y - cfg.small_character_y
        self.completion_label.y = self.reset_label.y - cfg.small_character_y
        self.update_labels()
    
    # draw the splits and labels
    def draw(self):
        if not cfg.hide_splits:
            for s in self.splits:
                s.draw()
        self.label_batch.draw()
screen = SplitContainer()

# thread class for watching the tasklist
class TaskThread(threading.Thread):
    def run(self):
        while True:
            process = cfg.exe
            taskList = os.popen("tasklist").readlines()
            found = False
            for task in taskList:
                if task[0:len(process)] == process:
                    mem.new_pid = int(task[29:34])
                    found = True
                    break
            if not found:
                mem.new_pid = 0
            time.sleep(1)

# store key presses into the key dict
@window.event
def on_key_press(symbol, modifiers):
  key.hitKey(symbol)

# draw the splits on screen draw
@window.event
def on_draw():
  window.clear()
  screen.draw()

# backup and save the config on exit
@window.event
def on_close():
  screen.backup("_e")
  cfg.save_config(window)

# read the config and run the code
cfg.read_config(window, screen)
def update(dt):
    if mem.new_pid == 0:
        mem.port = None
    if mem.new_pid > 0:
        mem.parse_memory(screen)
    elif screen.maps_played > 0:
        screen.reset_splits()
    screen.update()

taskThread = TaskThread(daemon=True)
taskThread.start()

pyglet.clock.schedule_interval(update, 1.) # updates once per second
pyglet.app.run()

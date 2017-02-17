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

# pyglet stuff
pyglet.options['debug_gl'] = False
label = pyglet.text.Label

# might use for tracking sr40 / sr50 inputs later
#def keyHitGlobal(key):
#  return win32api.GetAsyncKeyState(ord(key)) != 0

import key
from dtime import dTime
import memory as mem
from split import split
import cfg

cfg.init()
window = pyglet.window.Window(width=cfg.WindowWidth, height=cfg.WindowHeight, caption='krafSplit')

# container for it all
class _screen_:
  labelBatch = pyglet.graphics.Batch()
  currentTime = dTime()
  totalTime = dTime()
  prevTotal = dTime()
  sumOfBest = dTime()
  accruedTime = dTime()
  prevAccrued = dTime()
  runningMap = 0
  totalTimeLabel = label()
  currentTimeLabel = label()
  bestTimeLabel = label()
  accruedTimeLabel = label()
  splits = []
  doneIntermission = 0
  title = ""
  titleLabel = label()
  subTitle = ""
  subTitleLabel = label()
  completionLabel = label()
  resetLabel = label()
  sumOfBestLabel = label()
  attempts = 0
  mapsPlayed = 0
  currentMap = 0
  
  def __init__(self):
    self.labelBatch = pyglet.graphics.Batch()
    self.currentTime = dTime()
    self.totalTime = dTime()
    self.prevTotal = dTime()
    self.sumOfBest = dTime()
    self.prevAccrued = dTime()
    self.accruedTime = dTime()
    self.runningMap = 0
    self.title = "Untitled"
    self.titleLabel       = label(self.title,    font_name=cfg.fontName, font_size=cfg.FontSize,      x=cfg.XPadding,                   y=cfg.WindowHeight - cfg.YPadding,               anchor_x='left',  anchor_y='top',    color=cfg.titleColor,       batch=self.labelBatch)
    self.attemptsLabel    = label("0",           font_name=cfg.fontName, font_size=cfg.FontSize,      x=cfg.WindowWidth - cfg.XPadding, y=self.titleLabel.y,                             anchor_x='right', anchor_y='top',    color=cfg.attemptsColor,    batch=self.labelBatch)
    self.subTitleLabel    = label(self.subTitle, font_name=cfg.fontName, font_size=cfg.SmallFontSize, x=cfg.XPadding,                   y=self.titleLabel.y - cfg.CharacterY,            anchor_x='left',  anchor_y='top',    color=cfg.subTitleColor,    batch=self.labelBatch)
    self.totalTimeLabel   = label("0:00",        font_name=cfg.fontName, font_size=cfg.BigFontSize,   x=cfg.WindowWidth - cfg.XPadding, y=self.subTitleLabel.y - cfg.SmallCharacterY,    anchor_x='right', anchor_y='top',    color=cfg.timeNeutralColor, batch=self.labelBatch)
    self.sumOfBestLabel   = label("",            font_name=cfg.fontName, font_size=cfg.BigFontSize,   x=cfg.XPadding,                   y=self.subTitleLabel.y - cfg.SmallCharacterY,    anchor_x='left',  anchor_y='top',    color=cfg.timeBestColor,    batch=self.labelBatch)
    self.bestTimeLabel    = label("",            font_name=cfg.fontName, font_size=cfg.SmallFontSize, x=cfg.XPadding,                   y=self.sumOfBestLabel.y - cfg.BigCharacterY,     anchor_x='left',  anchor_y='top',    color=cfg.timeBestColor,    batch=self.labelBatch)
    self.currentTimeLabel = label("0.00",        font_name=cfg.fontName, font_size=cfg.SmallFontSize, x=cfg.WindowWidth - cfg.XPadding, y=self.totalTimeLabel.y - cfg.BigCharacterY,     anchor_x='right', anchor_y='top',    color=cfg.timeNeutralColor, batch=self.labelBatch)
    self.resetLabel       = label("",            font_name=cfg.fontName, font_size=cfg.SmallFontSize, x=cfg.WindowWidth - cfg.XPadding, y=self.currentTimeLabel.y - cfg.SmallCharacterY, anchor_x='right', anchor_y='top',    color=cfg.resetsColor,      batch=self.labelBatch)
    self.completionLabel  = label("",            font_name=cfg.fontName, font_size=cfg.SmallFontSize, x=cfg.WindowWidth - cfg.XPadding, y=self.resetLabel.y - cfg.SmallCharacterY,       anchor_x='right', anchor_y='top',    color=cfg.completionColor,  batch=self.labelBatch)
    self.accruedTimeLabel = label("0:00",        font_name=cfg.fontName, font_size=cfg.SmallFontSize, x=cfg.XPadding,                   y=cfg.YPadding,                                  anchor_x='left',  anchor_y='bottom', color=cfg.timeNeutralColor, batch=self.labelBatch)
    self.splits = []
    self.doneIntermission = 0
    self.attempts = 0
    self.mapsPlayed = 0
    self.currentMap = 0
  
  def updateLabels(self):
    self.attemptsLabel.text = str(self.attempts)
    if self.mapsPlayed == 0:
      self.totalTimeLabel.color = cfg.timeNeutralColor
      self.bestTimeLabel.text = ""
      self.resetLabel.text = ""
    else:
      if len(self.splits) >= self.mapsPlayed:
        self.bestTimeLabel.text = self.splits[self.mapsPlayed - 1].bestTime.toString()
        if self.bestTimeLabel.text == "0.00":
          self.bestTimeLabel.text = "---"
        self.resetLabel.text = self.splits[self.mapsPlayed - 1].resetText()
      if len(self.splits) < self.mapsPlayed:
        better = 0
      else:
        better = self.totalTime.compareSecs(self.splits[self.mapsPlayed - 1].prevTotal)
      if better < 0:
        self.totalTimeLabel.color = cfg.timeBadColor
      elif better > 0:
        self.totalTimeLabel.color = cfg.timeGoodColor
      else:
        self.totalTimeLabel.color = cfg.timeNeutralColor
    if self.mapsPlayed == 0:
      self.currentTimeLabel.color = cfg.timeNeutralColor
    else:
      if len(self.splits) < self.mapsPlayed:
        better = 0
      else:
        better = self.currentTime.compareSecs(self.splits[self.mapsPlayed - 1].prevTime)
      if better < 0:
        self.currentTimeLabel.color = cfg.timeBadColor
      elif better > 0:
        self.currentTimeLabel.color = cfg.timeGoodColor
      else:
        self.currentTimeLabel.color = cfg.timeNeutralColor
    self.totalTimeLabel.text   = self.totalTime.toString(centi=False, forceM=True)
    self.currentTimeLabel.text = self.currentTime.toString()
    self.accruedTimeLabel.text = self.accruedTime.toString(centi=True, forceM=True)
  
  def updateTitle(self, newTitle="DooM"):
    self.title = newTitle
    self.titleLabel.text = self.title
    self.buildSplits()
  
  def updateSubTitle(self, newTitle=""):
    self.subTitle = newTitle
    self.subTitleLabel.text = self.subTitle
    self.buildSplits()
  
  def saveSplits_(self, fileName, changeName=True):
    if changeName:
      cfg.lastFile = fileName
    
    f = open(fileName, 'w')
    
    print(self.title, file=f)
    print(self.subTitle, file=f)
    print(self.attempts, file=f)
    print(self.accruedTime.toSimpleString(), file=f)
    
    for s in self.splits:
      print(s.name + "; " + s.prevTime.toSimpleString() + " " + s.bestTime.toSimpleString() + " " + str(s.resets) + " " + str(s.arrivals), file=f)
    
    f.close()
  
  def saveSplits(self):
    if cfg.lastFile != "":
      self.backup("_s")
      self.saveSplits_(cfg.lastFile)
    else:
      savePath = filedialog.asksaveasfilename(defaultextension=".ks", filetypes=[('krafsplit files', '.ks')])
      if savePath == "":
        return
      self.saveSplits_(savePath)
  
  def backup(self, c="_"):
    if cfg.lastFile != "":
      self.saveSplits_(cfg.lastFile + c, changeName=False)
  
  def readSplits(self, fileName):
    if not os.path.isfile(fileName):
      return
    self.accruedTime.zero()
    self.splits.clear()
    cfg.lastFile = fileName
    f = open(fileName, 'r')
    self.updateTitle(f.readline().rstrip())
    self.updateSubTitle(f.readline().rstrip())
    self.attempts = int(f.readline().rstrip())
    self.prevAccrued = dTime(text=f.readline().rstrip())
    self.accruedTime.copy(self.prevAccrued)
    for line in f:
      l = line.rstrip()
      if len(self.splits) > 0:
        self.splits.append(split(l, sum=self.splits[-1].prevTotal))
      else:
        self.splits.append(split(l))
    self.buildSplits()
    self.backup()
  
  def finishRun(self):
    if self.splits[-1].improved():
      for s in self.splits:
        s.overwrite()
  
  def makeSumOfBest(self):
    self.sumOfBest.zero()
    for s in self.splits:
      if not s.bestTime.exists():
        self.sumOfBest.zero()
        break
      self.sumOfBest.addSecs(s.bestTime)
    self.sumOfBestLabel.text = self.sumOfBest.toString(centi=False, forceM=True)
  
  def update(self):        
    if key.hit(pykey.C):
      self.accruedTime.zero()
      self.prevAccrued.zero()
      self.splits = []
      self.attempts = 0
      self.updateSubTitle()
      self.updateTitle()
      self.buildSplits()
      cfg.lastFile = ""
    
    if key.hit(pykey.S):
      self.saveSplits()
    
    if key.hit(pykey.T):
      title = simpledialog.askstring("", "Title")
      if title == "" or title == None:
        title = "Untitled"
      self.updateTitle(title)
    
    if key.hit(pykey.Y):
      subTitle = simpledialog.askstring("", "Sub Title")
      if subTitle == None:
        subTitle = ""
      self.updateSubTitle(subTitle)
    
    if key.hit(pykey.H):
      cfg.hideSplits = int(cfg.hideSplits == 0)
      self.buildSplits()
    
    if key.hit(pykey.O):
      openPath = filedialog.askopenfilename(defaultextension=".ks")
      if openPath != "":
        self.readSplits(openPath)
    
    if key.hit(pykey.N):
      n = simpledialog.askstring("", "Split Count")
      if n is not None:
        n = int(n)
      else:
        n = 0
      while len(self.splits) < n:
        self.splits.append(split(new=True))
      if n == 0:
        self.splits = []
      else:
        self.splits = self.splits[:n]
      cfg.lastFile = ""
      self.buildSplits()
    
    if mem.recording == 1 and mem.port is not None:
      if mem.intermission == 1 and self.doneIntermission == 0:
        self.currentTime.fromTics(mem.tics)
        self.totalTime.copy(self.currentTime)
        self.totalTime.addSecs(self.prevTotal)
        self.doneIntermission = 1
        if self.mapsPlayed <= len(self.splits):
          self.splits[self.mapsPlayed - 1].end(self)
        if self.mapsPlayed == len(self.splits):
          self.finishRun()
        self.makeSumOfBest()
      elif mem.intermission == 0:
        self.doneIntermission = 0
      if self.currentMap != mem.mapNumber:
        self.mapsPlayed += 1
        if len(self.splits) >= self.mapsPlayed:
          self.splits[self.mapsPlayed - 1].arrivals += 1
        if self.mapsPlayed == 1:
          self.attempts += 1
        self.currentMap = mem.mapNumber
        self.doneIntermission = 0
        self.prevTotal.copy(self.totalTime)
        self.prevAccrued.copy(self.accruedTime)
      self.currentTime.fromTics(mem.tics)
      self.totalTime.copy(self.currentTime)
      self.totalTime.addSecs(self.prevTotal)
      self.accruedTime.copy(self.prevAccrued)
      self.accruedTime.add(self.currentTime)
      
      if mem.monsterAlive == 0:
        self.completionLabel.text = "K"
      elif mem.killCount == mem.monsterTotal:
        self.completionLabel.text = "k"
      else:
        self.completionLabel.text = ""
      if mem.itemFound == mem.itemTotal:
        self.completionLabel.text += "I"
      else:
        self.completionLabel.text += ""
      if mem.secretFound == mem.secretTotal:
        self.completionLabel.text += "S"
      else:
        self.completionLabel.text += ""
      
      self.updateLabels()
  
  def resetSplits(self):
    if len(self.splits) >= self.mapsPlayed and self.mapsPlayed > 0:
      if not self.splits[self.mapsPlayed - 1].ended or len(self.splits) > self.mapsPlayed:
        self.splits[self.mapsPlayed - 1].resets += 1
    mem.recording = 0
    self.mapsPlayed = 0
    mem.mapNumber = 0
    self.currentMap = 0
    mem.tics = 0
    self.totalTime.zero()
    self.prevTotal.zero()
    self.currentTime.zero()
    self.completionLabel.text = ""
    self.prevAccrued.copy(self.accruedTime)
    self.updateLabels()
    
    for s in self.splits:
      s.reset()
    self.buildSplits()
  
  def buildSplits(self):
    subTitleAdjust = cfg.SmallCharacterY
    if self.subTitle == "":
      subTitleAdjust = 0
    
    n = len(self.splits)
    i = 0
    for s in self.splits:
      s.build(self.titleLabel.y - subTitleAdjust - (i + 1) * cfg.CharacterY)
      i += 1
    if cfg.hideSplits:
      n = 0
    
    self.makeSumOfBest()
    
    self.totalTimeLabel.y = self.titleLabel.y - subTitleAdjust - cfg.CharacterY * (n + 1)
    self.currentTimeLabel.y = self.totalTimeLabel.y - cfg.BigCharacterY
    self.sumOfBestLabel.y = self.totalTimeLabel.y
    self.bestTimeLabel.y = self.currentTimeLabel.y
    self.resetLabel.y = self.currentTimeLabel.y - cfg.SmallCharacterY
    self.completionLabel.y = self.resetLabel.y - cfg.SmallCharacterY
    self.updateLabels()
    
  def draw(self):
    if not cfg.hideSplits:
      for s in self.splits:
        s.draw()
    self.labelBatch.draw()
Screen = _screen_()

class TaskThread(threading.Thread):
  def run(self):
    while True:
      process = cfg.exe
      taskList = os.popen("tasklist").readlines()
      found = False
      for task in taskList:
        if task[0:len(process)] == process:
          mem.newPid = int(task[29:34])
          found = True
          break
      if not found:
        mem.newPid = 0
      time.sleep(1)

@window.event
def on_key_press(symbol, modifiers):
  key.hitKey(symbol)

@window.event
def on_draw():
  window.clear()
  Screen.draw()

@window.event
def on_close():
  Screen.backup("_e")
  cfg.saveConfig(window)

cfg.readConfig(window, Screen)
def update(dt):
  if mem.newPid == 0:
    mem.port = None
  if mem.newPid > 0:
    mem.parseMemory(Screen)
  elif Screen.mapsPlayed > 0:
    Screen.resetSplits()
  Screen.update()

taskThread = TaskThread(daemon=True)
taskThread.start()

pyglet.clock.schedule_interval(update, 1.)
pyglet.app.run()

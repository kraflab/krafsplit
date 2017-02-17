from dtime import dTime
import cfg
import pyglet
label = pyglet.text.Label

class split:
  name = ""
  bestTime  = dTime()
  prevTime  = dTime()
  thisTime  = dTime()
  thisTotal = dTime()
  prevTotal = dTime()
  nameLabel  = label()
  totalLabel = label()
  resets   = 0
  arrivals = 0
  ended = False
  best  = False
  better = 0
  betterTotal = 0
  
  def __init__(self, line=None, sum=None, new=False):
    self.nameLabel  = label("", font_name=cfg.fontName, font_size=cfg.SmallFontSize, x=cfg.XPadding, y=cfg.WindowHeight, anchor_x='left',  anchor_y='top', color=cfg.splitNameColor)
    self.totalLabel = label("", font_name=cfg.fontName, font_size=cfg.FontSize,      x=0,            y=cfg.WindowHeight, anchor_x='right', anchor_y='top', color=cfg.timeNeutralColor)
    self.deltaLabel = label("", font_name=cfg.fontName, font_size=cfg.FontSize,      x=0,            y=cfg.WindowHeight, anchor_x='right', anchor_y='top', color=cfg.timeNeutralColor)
    self.ended = False
    self.best  = False
    self.better = 0
    self.betterTotal = 0
    self.resets = 0
    self.arrivals = 0
    if new == True:
      self.name = '?'
      self.bestTime = dTime()
      self.prevTime = dTime()
      self.thisTime = dTime()
      self.prevTotal = dTime()
      self.thisTotal = dTime()
    elif line is None:
      self.name = ""
      self.bestTime = dTime()
      self.prevTime = dTime()
      self.thisTime = dTime()
      self.prevTotal = dTime()
      self.thisTotal = dTime()
    else:
      sub = line.split(";")
      self.name = sub[0]
      sub = sub[1].lstrip().split(" ")
      if sub[0] == "-":
        self.bestTime = dTime()
        self.prevTime = dTime()
        self.thisTime = dTime()
        self.prevTotal = dTime()
        self.thisTotal = dTime()
      else:
        self.prevTime = dTime(text=sub[0])
        self.bestTime = dTime(text=sub[1])
        self.prevTotal = dTime(sum)
        self.prevTotal.addSecs(self.prevTime)
        self.thisTime = dTime()
        self.thisTotal = dTime()
        self.resets = int(sub[2])
        self.arrivals = int(sub[3])
  
  def improved(self):
    return self.thisTotal.betterThan(self.prevTotal)
  
  def overwrite(self):
    self.prevTotal.copy(self.thisTotal)
    self.prevTime.copy(self.thisTime)
  
  def resetText(self):
    return str(self.arrivals - 1 - self.resets) + "/" + str(self.arrivals - 1)
  
  def reset(self):
    self.thisTotal.zero()
    self.thisTime.zero()
    self.best = 0
    self.better = 0
    self.betterTotal = 0
    self.ended = False
  
  def build(self, y=0):
    if y > 0:
      self.nameLabel.y = y
      self.totalLabel.y = y
      self.deltaLabel.y = y
    self.nameLabel.text = self.name
    if self.thisTotal.exists():
      self.totalLabel.text = self.thisTotal.toString(centi=False, forceM=True)
    elif self.prevTotal.exists():
      self.totalLabel.text = self.prevTotal.toString(centi=False, forceM=True)
    else:
      self.totalLabel.text = "---"
    self.totalLabel.x = cfg.WindowWidth - cfg.XPadding
    self.deltaLabel.x = cfg.WindowWidth - cfg.XPadding - cfg.CharacterX * 4
    
    if self.best:
      self.totalLabel.color = cfg.timeBestColor
    elif self.betterTotal > 0:
      self.totalLabel.color = cfg.timeBadColor
    elif self.betterTotal < 0:
      self.totalLabel.color = cfg.timeGoodColor
    else:
      self.totalLabel.color = cfg.timeNeutralColor
    
    if not self.ended:
      self.deltaLabel.text = ""
    elif self.betterTotal == 0:
      self.deltaLabel.text = "---"
      self.deltaLabel.color = cfg.timeNeutralColor
    else:
      self.deltaLabel.text = str(self.betterTotal)
      if self.betterTotal > 0:
        self.deltaLabel.text = "+" + self.deltaLabel.text
        self.deltaLabel.color = cfg.timeBadColor
      else:
        self.deltaLabel.color = cfg.timeGoodColor
  
  def end(self, screen):
    if not self.ended:
      self.ended = True
      self.thisTime.copy(screen.currentTime)
      self.thisTotal.copy(screen.totalTime)
      if self.thisTime.betterThan(self.bestTime):
        self.bestTime.copy(self.thisTime)
        self.best = True
      if self.prevTotal.exists():
        self.betterTotal = self.thisTotal.deltaSecs(self.prevTotal)
      else:
        self.betterTotal = 0
      if self.prevTime.exists():
        self.better = self.thisTime.deltaSecs(self.prevTime)
      else:
        self.better = 0
    self.build()
  
  def draw(self):
    self.nameLabel.draw()
    self.totalLabel.draw()
    self.deltaLabel.draw()

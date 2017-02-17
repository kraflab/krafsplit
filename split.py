from dtime import dTime
import cfg
import pyglet
label = pyglet.text.Label

class Split:
    name = ""
    best_time  = dTime()
    prev_time  = dTime()
    this_time  = dTime()
    this_total = dTime()
    prev_total = dTime()
    name_label  = label()
    total_label = label()
    resets       = 0
    arrivals     = 0
    better       = 0
    better_total = 0
    ended = False
    best  = False
    
    def __init__(self, line=None, sum=None, new=False):
        self.name_label  = label("", font_name=cfg.font_name, font_size=cfg.small_font_size, x=cfg.x_padding, y=cfg.window_height, anchor_x='left',  anchor_y='top', color=cfg.split_name_color)
        self.total_label = label("", font_name=cfg.font_name, font_size=cfg.font_size,       x=0,             y=cfg.window_height, anchor_x='right', anchor_y='top', color=cfg.time_neutral_color)
        self.delta_label = label("", font_name=cfg.font_name, font_size=cfg.font_size,       x=0,             y=cfg.window_height, anchor_x='right', anchor_y='top', color=cfg.time_neutral_color)
        self.ended = False
        self.best  = False
        self.resets       = 0
        self.arrivals     = 0
        self.better       = 0
        self.better_total = 0
        if new == True:
            self.name = '?'
            self.best_time  = dTime()
            self.prev_time  = dTime()
            self.this_time  = dTime()
            self.prev_total = dTime()
            self.this_total = dTime()
        elif line is None:
            self.name = ""
            self.best_time  = dTime()
            self.prev_time  = dTime()
            self.this_time  = dTime()
            self.prev_total = dTime()
            self.this_total = dTime()
        else:
            sub = line.split(";")
            self.name = sub[0]
            sub = sub[1].lstrip().split(" ")
            if sub[0] == "-":
                self.best_time  = dTime()
                self.prev_time  = dTime()
                self.this_time  = dTime()
                self.prev_total = dTime()
                self.this_total = dTime()
            else:
                self.prev_time = dTime(text=sub[0])
                self.best_time = dTime(text=sub[1])
                self.prev_total = dTime(sum)
                self.prev_total.add_secs(self.prev_time)
                self.this_time  = dTime()
                self.this_total = dTime()
                self.resets   = int(sub[2])
                self.arrivals = int(sub[3])
    
    # return true if the this total time is better than the previous time
    def improved(self):
        return self.this_total.better_than(self.prev_total)
    
    # replace the previous times with these times
    def overwrite(self):
        self.prev_total.copy(self.this_total)
        self.prev_time.copy(self.this_time)
    
    # text for the success rate of this split
    def resetText(self):
        return str(self.arrivals - 1 - self.resets) + "/" + str(self.arrivals - 1)
    
    # reset the split to its starting configuration
    def reset(self):
        self.this_total.zero()
        self.this_time.zero()
        self.best = 0
        self.better = 0
        self.better_total = 0
        self.ended = False
    
    # set up label text and location
    def build(self, y=0):
        if y > 0:
            self.name_label.y = y
            self.total_label.y = y
            self.delta_label.y = y
        self.name_label.text = self.name
        if self.this_total.exists():
            self.total_label.text = self.this_total.to_string(centi=False, forceM=True)
        elif self.prev_total.exists():
            self.total_label.text = self.prev_total.to_string(centi=False, forceM=True)
        else:
            self.total_label.text = "---"
        self.total_label.x = cfg.window_width - cfg.x_padding
        self.delta_label.x = cfg.window_width - cfg.x_padding - cfg.character_x * 4
        
        if self.best:
            self.total_label.color = cfg.time_best_color
        elif self.better_total > 0:
            self.total_label.color = cfg.time_bad_color
        elif self.better_total < 0:
            self.total_label.color = cfg.time_good_color
        else:
            self.total_label.color = cfg.time_neutral_color
        
        if not self.ended:
            self.delta_label.text = ""
        elif self.better_total == 0:
            self.delta_label.text = "---"
            self.delta_label.color = cfg.time_neutral_color
        else:
            self.delta_label.text = str(self.better_total)
            if self.better_total > 0:
                self.delta_label.text = "+" + self.delta_label.text
                self.delta_label.color = cfg.time_bad_color
            else:
                self.delta_label.color = cfg.time_good_color
    
    # end this split and check for best / etc
    def end(self, screen):
        if not self.ended:
            self.ended = True
            self.this_time.copy(screen.current_time)
            self.this_total.copy(screen.total_time)
            if self.this_time.better_than(self.best_time):
                self.best_time.copy(self.this_time)
                self.best = True
            if self.prev_total.exists():
                self.better_total = self.this_total.delta_secs(self.prev_total)
            else:
                self.better_total = 0
            if self.prev_time.exists():
                self.better = self.this_time.delta_secs(self.prev_time)
            else:
                self.better = 0
        self.build()
    
    # draw the labels
    def draw(self):
        self.name_label.draw()
        self.total_label.draw()
        self.delta_label.draw()

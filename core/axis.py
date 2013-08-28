import math

class Axis(object):
    def __init__(self, min, max, **kwarg):
        self.min = min
        self.max = max
        self.wrap = False
        
        if "wrap" in kwarg: self.wrap = kwarg["wrap"]
        
        target_tickcount = 10.0
        tick = (max - min) / target_tickcount
        self.tickdecimals = int(-math.floor(math.log10(tick)))
        self.ticksize = round(tick, self.tickdecimals)

    def map(self, v):
        return (v - self.min) / (self.max - self.min)

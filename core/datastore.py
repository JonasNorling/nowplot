import numpy as np

ARRAYSIZE = 1000
XTYPE = "f8"
YTYPE = "f4"

class Subseries(object):
    def __init__(self):
        self.array = np.zeros(ARRAYSIZE, dtype=[("x", XTYPE), ("y", YTYPE)])
        self.xrange = [None, None]
        self.yrange = [None, None]
        self.pos = 0
        self.full = False
        
        
class Series(object):
    def __init__(self, name):
        self.name = name
        self.subseries = []
        self.subseries.append(Subseries())
        self.currentSubseries = self.subseries[-1]
        
    def addSample(self, x, y):
        if self.currentSubseries.pos >= ARRAYSIZE:
            # Start a new sub-series
            self.currentSubseries.full = True
            self.subseries.append(Subseries())
            self.currentSubseries = self.subseries[-1]
            
        self.currentSubseries.array[self.currentSubseries.pos] = (x, y)
        self.currentSubseries.pos += 1
        if self.currentSubseries.xrange[0] is None:
            self.currentSubseries.xrange[0] = x
        self.currentSubseries.xrange[1] = x # x is monotonic!


class Datastore(object):
    def __init__(self):
        self.series = []
        pass
    
    def addSeries(self, name):
        s = Series(name)
        self.series.append(s)
        return s

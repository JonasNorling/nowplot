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
        """Add an absolute sample value at the point (x,y), where x typically is monotonic time"""
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
    
    def addSeries(self, name, **kwargs):
        s = Series(name, **kwargs)
        self.series.append(s)
        return s

    def close(self, x):
        """Indicate that no more data will be added before this X position"""
        # We now need to pad all series with zeros up to this point in time. Crap.
        pass
    
import threading
import time
import random

class Noisegen(threading.Thread):
    def __init__(self, datastore, seriesname = "random", interval = 0.5, distribution = (0.0, 0.2)):
        threading.Thread.__init__(self)
        self.stopped = False
        
        self.interval = interval
        self.distribution = distribution
        self.series = datastore.addSeries(seriesname)
        self.random = random.Random()
    
    def stop(self):
        self.stopped = True
        
    def run(self):
        while not self.stopped:
            value = self.random.gauss(*self.distribution)
            self.series.addSample(time.time(), value)
            time.sleep(self.interval)
            
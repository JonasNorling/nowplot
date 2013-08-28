import threading
import time

# Whence cometh X axis? - time - read as column
# Option to skip heading lines
# Option to extract names from header
# Regex parsing
# Splitting by whitespace or character
# Waiting blockingly on a pipe
# inotify or poll file

class FileRead(threading.Thread):
    def __init__(self, datastore, file, **kwargs):
        threading.Thread.__init__(self)
        self.datastore = datastore
        self.series = []
        self.stopped = False
        self.file = file
        self.lineno = 0
        self.sampleno = 0
        
        self.skiplines = 0
        self.readheader = False
        if "skiplines" in kwargs:
            self.skiplines = kwargs["skiplines"]
        if "readheader" in kwargs:
            self.readheader = True
        
    def stop(self):
        self.stopped = True
        
    def run(self):
        while not self.stopped:
            line = self.file.readline()
            self.lineno += 1
            
            if self.lineno <= self.skiplines:
                continue
            
            # FIXME: Allow fancier splittings
            items = line.split()
            
            if self.readheader and self.sampleno == 0:
                for item in items:
                    print("Found series %s" % item)
                    series = self.datastore.addSeries(item)
                    self.series.append(series)
            
            # This is too fragile!
            for i, item in enumerate(items):
                try:
                    value = float(item)
                    self.series[i].addSample(self.sampleno, value)
                except ValueError:
                    pass
            
            self.sampleno += 1
            
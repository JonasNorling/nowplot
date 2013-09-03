import threading
import time

class FileRead(threading.Thread):
    def __init__(self, datastore, file, **kwargs):
        threading.Thread.__init__(self)
        self.datastore = datastore
        self.series = []
        self.stopped = False
        self.file = file
        self.lineno = 0
        self.sampleno = 0
        self.separator = None # Whitespace
        
        self.skiplines = 0
        self.readheader = False
        if "skiplines" in kwargs:
            self.skiplines = kwargs["skiplines"]
        if "readheader" in kwargs:
            self.readheader = kwargs["readheader"]
        if "separator" in kwargs:
            self.separator = kwargs["separator"]
        
    def stop(self):
        self.stopped = True
        
    def run(self):
        while not self.stopped:
            line = self.file.readline()
            self.lineno += 1
            
            if self.lineno <= self.skiplines:
                continue
            
            items = line.split(self.separator)
            
            # If this is the first line, parse the header
            if self.readheader and self.lineno == self.skiplines + 1:
                for item in items:
                    series = self.datastore.addSeries(item)
                    self.series.append(series)
                print("Found series: %s" % ",".join(items))
                continue
            
            # Add samples from this line            
            for i, item in enumerate(items):
                if i == len(self.series):
                    # No series created for this column yet, create one
                    if not self.readheader:
                        series = self.datastore.addSeries("%d" % (i+1))
                        self.series.append(series)
                        print("Created series for column %d" % (i+1))
                try:
                    value = float(item)
                    self.series[i].addSample(self.sampleno, value)
                except ValueError:
                    pass
            
            self.sampleno += 1
            
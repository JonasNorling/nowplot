import cairo
import math

class Seriesdata(object):
    def __init__(self):
        self.lastPlottedSample = 0
        self.lastPos = None


class Plotter(object):
    def __init__(self, surface, size, datastore, xAxis, yAxis, profiles):
        self.surface = surface
        self.size = size
        self.datastore = datastore
        self.profiles = profiles
        self.highestX = 0

        self.xAxis = xAxis
        self.yAxis = yAxis

        self.ctx = cairo.Context(self.surface)
        
        # Flip coordinate system upside-down
        self.ctx.set_matrix(cairo.Matrix(1, 0, 0, -1, 0, self.size[1]))
        
        self.seriesdata = {}

    def setXAxis(self, xAxis):
        self.xAxis = xAxis

    def setYAxis(self, yAxis):
        self.yAxis = yAxis
    
    def fade(self):
        self.ctx.save()
        self.ctx.set_operator(cairo.OPERATOR_DEST_OUT)
        self.ctx.set_source_rgba(0.0, 0.0, 0.0, 0.05)
        self.ctx.paint()
        self.ctx.restore()
        
    def draw(self):
        """Draw something if we want to, return damaged area"""
        damage = None
        
        # FIXME: We may miss the end of a sub-series when the transition to a new sub-series is made.
        for series in self.datastore.series:
            if not series.name in self.profiles:
                continue
            profile = self.profiles[series.name]
            
            subseries = series.currentSubseries
            try:
                seriesdata = self.seriesdata[series]
            except KeyError:
                seriesdata = Seriesdata()
                self.seriesdata[series] = seriesdata
            lastSample = subseries.pos
            
            self.ctx.set_source_rgba(*profile.color)
            if profile.lineWidth is not None: self.ctx.set_line_width(profile.lineWidth)
            
            pos = None
            if seriesdata.lastPos is not None:
                pos = seriesdata.lastPos
            
            for n in range(seriesdata.lastPlottedSample, lastSample):
                damage = True
                sample = subseries.array[n]
                
                x_value = sample["x"]
                y_value = sample["y"]
                if self.xAxis.wrap:
                    x_value = (x_value - self.xAxis.min) % (self.xAxis.max - self.xAxis.min) + self.xAxis.min
                lastpos = pos
                pos = (self.xAxis.map(x_value) * self.size[0], self.yAxis.map(y_value) * self.size[1])
                
                if lastpos is not None and profile.lineWidth is not None:
                    if pos[0] >= lastpos[0]:
                        self.ctx.move_to(*lastpos)
                        self.ctx.line_to(*pos)
                        self.ctx.stroke()
                if profile.point:
                    self.ctx.arc(pos[0], pos[1], profile.point, 0, math.pi*2)
                    self.ctx.fill()
                
                if sample["x"] > self.highestX:
                    if sample["x"] // 100 > self.highestX // 100:
                        self.fade()
                    self.highestX = sample["x"]
                
            seriesdata.lastPlottedSample = lastSample
            if pos is not None:
                seriesdata.lastPos = pos
            
        return damage
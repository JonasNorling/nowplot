from __future__ import division
import gtk
import cairo
import gobject
import math
from plotter import Plotter
from overlayplotter import OverlayPlotter
from core.axis import Axis

class PlotWidget(gtk.DrawingArea):
    def __init__(self, datastore, profiles, xAxis=None, yAxis=None):
        gtk.DrawingArea.__init__(self)
        self.backgroundcolor = (0.4, 0.15, 0.3, 1)
        self.datastore = datastore
        self.profiles = profiles
        self.x_wrap = False
        self.realized = False
        self.connect("expose-event", self.on_expose_event)
        self.connect("configure-event", self.on_configure_event)
        self.connect("realize", self.on_realize)

        self.plotter = None
        self.plotbuffer = None
        self.overlaybuffer = None

        if xAxis is None:
            xAxis = Axis(0, 600, wrap=True) 
        if yAxis is None:
            yAxis = Axis(-1, 1)
            
        self.xAxis = xAxis 
        self.yAxis = yAxis

        gobject.timeout_add(50, self.draw)
        
    def setXAxis(self, xAxis):
        self.xAxis = xAxis
        if self.realized:
            self.plotter.setXAxis(self.xAxis)
            self.overlayplotter.setXAxis(self.xAxis)
            self.on_realize()
            self.queue_draw()

    def setYAxis(self, yAxis):
        self.yAxis = yAxis
        if self.realized:
            self.plotter.setYAxis(self.yAxis)
            self.overlayplotter.setYAxis(self.yAxis)
            self.on_realize()
            self.queue_draw()
        
    def on_realize(self, widget=None):
        self.realized = True
        winctx = self.window.cairo_create()
        
        if self.plotbuffer is None:
            self.plotsize = (1600, 960)
            self.plotbuffer = winctx.get_target().create_similar(cairo.CONTENT_COLOR_ALPHA,
                                                                 self.plotsize[0], self.plotsize[1])
            self.plotter = Plotter(self.plotbuffer, self.plotsize, self.datastore,
                                   self.xAxis, self.yAxis, self.profiles)
        overlaysize = self.size
        self.overlaybuffer = winctx.get_target().create_similar(cairo.CONTENT_COLOR_ALPHA,
                                                             self.size[0], self.size[1])
        self.overlayplotter = OverlayPlotter(self.overlaybuffer, overlaysize, self.xAxis, self.yAxis)
        self.overlayplotter.draw()

    def on_configure_event(self, widget, event):
        self.size = (event.width, event.height)
        self.on_realize(widget)

    def on_expose_event(self, widget, event):
        winctx = self.window.cairo_create()
        winctx.set_source_rgba(*self.backgroundcolor)
        winctx.paint()
        winctx.save()
        winctx.scale(self.size[0] / self.plotsize[0], self.size[1] / self.plotsize[1])
        winctx.set_source_surface(self.plotbuffer)
        winctx.paint()
        winctx.restore()
        winctx.set_source_surface(self.overlaybuffer)
        winctx.paint_with_alpha(1.0)

    def draw(self):
        if self.plotter is not None:
            damage = self.plotter.draw()
            if damage is not None:
                # FIXME: Would keeping better track of the damage increase performance?
                self.queue_draw()
        return True # Keep on timering
    
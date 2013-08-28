import gtk
from plotwin import PlotWindow
from plotwidget import PlotWidget

class Gui(object):
    def __init__(self, datastore, profiles):
        self.datastore = datastore
        self.profiles = profiles
        gtk.gdk.threads_init()
        self.plotwidget = PlotWidget(self.datastore, self.profiles)
        self.plotwin = PlotWindow(self.plotwidget)
    
    def getMainPlotWidget(self):
        return self.plotwin.plot
    
    def run(self):
        self.plotwin.show_all()
    
        try:
            gtk.main()
        except KeyboardInterrupt:
            pass

import gtk

class PlotWindow(gtk.Window):
    def __init__(self, plotWidget):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_default_size(800, 480);
        self.connect("destroy", self.quit_callback)

        mainBox = gtk.HBox()
        self.add(mainBox)
        self.plot = plotWidget
        mainBox.pack_start(self.plot, True)

        self.show_all()

    def quit_callback(self, b):
        gtk.main_quit()

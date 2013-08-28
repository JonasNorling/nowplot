#!/usr/bin/python

from core.datastore import Datastore
from core.axis import Axis
from core.seriesprofile import SeriesProfile
from input.noisegen import Noisegen
from gui import Gui

if __name__ == "__main__":
    datastore = Datastore()
    n1 = Noisegen(datastore, "rand1")
    n2 = Noisegen(datastore, "rand2", 0.1, (-0.5, 0.05))
    n1.start()
    n2.start()
    
    gui = Gui(datastore, {"rand1": SeriesProfile(line=3, point=8, color="a0ffffff"),
                          "rand2": SeriesProfile(line=1, color="80ffff80")})
    gui.getMainPlotWidget().setXAxis(Axis(0, 60, wrap=True))
    gui.run()
    
    n1.stop()
    n2.stop()
    n1.join()
    n2.join()
    
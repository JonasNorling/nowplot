#!/usr/bin/python

from core.datastore import Datastore
from core.seriesprofile import SeriesProfile
from core.axis import Axis
from input.fileread import FileRead
from gui import Gui
import subprocess

if __name__ == "__main__":
    datastore = Datastore()
    
    process = subprocess.Popen(["vmstat", "-n", "1"], stdout=subprocess.PIPE)
    
    f = FileRead(datastore, process.stdout, skiplines=1, readheader=True)
    f.start()
    
    gui = Gui(datastore, {
                    "free": SeriesProfile(line=3),
                    "buff": SeriesProfile(line=3, color="ffff80"),
                    "cache": SeriesProfile(line=3, color="ff80ff")
                     })
    gui.getMainPlotWidget().setXAxis(Axis(0, 600, wrap=True))
    gui.getMainPlotWidget().setYAxis(Axis(0, 3000000))
    gui.run()
    
    f.stop()
    f.join()


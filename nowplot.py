#!/usr/bin/python
#
# Copyright 2013, Jonas Norling <jonas.norling@gmail.com>
#
# This software program is licensed under the GNU General Public License v2.
#

import optparse
import sys
import re
from core.datastore import Datastore
from core.seriesprofile import SeriesProfile
from core.axis import Axis
from input.fileread import FileRead
from gui import Gui

epilog=\
"""If no input file is specified, standard input it used. Implicitly discovered series are named with a decimal number from 1.
Letters in series specifications: l=line, p=point, lp=line and point, v=vertical line for non-zero samples (event).
Colors are given as six-digit hex strings (#ff6666 is a lovely shade of pink) or as an eight-digit string with alpha first.
"""
description=\
"Nowplot is a realtime data plotter, drawing an oscilloscope-like view of data samples."


def parseSeries(s):
    series = {}

    series_re = re.compile("(.*)=([lpv]+)([0123456789]+)?(:#(.*))?(:(.*))?")
    strings = s.split(",")

    for string in strings:
        match = series_re.match(string)
        if match is None:
            raise ValueError
        (name, type, width, crap, color, crap, label) = match.groups()
        
        line = None
        point = None
        
        if width is not None: width = int(width)
        if type is not None and "p" in type: point = width
        if type is not None and "l" in type: line = width

        series[name] = SeriesProfile(line=line, color=color, point=point)
    
    return series

if __name__ == '__main__':

    # Parse command line

    parser = optparse.OptionParser(usage="Usage: %prog [options] [file]",
                                   description=description, epilog=epilog)
    parser.add_option("-x", "--x-axis", dest="x_axis", default="-3:103",
                      help="X axis specification: <start>:<end> | auto", metavar="SPEC")
    parser.add_option("-y", "--y-axis", dest="y_axis", default="-3:103",
                      help="Y axis specification: <start>:<end> | auto", metavar="SPEC")
    parser.add_option("-s", "--series", dest="series", default="1=lp3:#a0ffffff,2=lp3:#a0ffff80,3=lp3:#a0ff80ff",
                      help="Data series specification: <name>=[{l|p|lp|v}[<width>]][:#<color>],...", metavar="SPEC")
    parser.add_option("-w", "--wrap", dest="wrap", default=False, action="store_true",
                      help="Wrap x axis, drawing samples in a modulo fashion")

    group = optparse.OptionGroup(parser, "Sample collection options")
    group.add_option("-W", "--watch", dest="watch", default=False, action="store_true",
                     help="Watch the input file for new lines. Default for stdin")
    group.add_option("-F", "--field-separator", dest="separator", default=None, metavar="FS",
                     help="Set the input field separator. Default is a whitespace")
    group.add_option("-t", "--time", dest="time", default=False, action="store_true",
                     help="Use current system time as X value")
    group.add_option("-c", "--count", dest="count", default=False, action="store_true",
                     help="Use sample count as X value")
    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    # Start doing stuff

    datastore = Datastore()
    
    infile = sys.stdin
    if len(args) > 0:
        infile = open(args[0])
    
    f = FileRead(datastore, infile, skiplines=0, readheader=False, separator=options.separator)
    f.start()
    
    (min, max) = options.x_axis.split(":")
    xAxis = Axis(float(min), float(max))
    (min, max) = options.y_axis.split(":")
    yAxis = Axis(float(min), float(max))
    
    if options.wrap:
        xAxis.wrap = True
    
    series = parseSeries(options.series)
    
    gui = Gui(datastore, series)
    gui.getMainPlotWidget().setXAxis(xAxis)
    gui.getMainPlotWidget().setYAxis(yAxis)
    gui.run()
    
    f.stop()
    f.join()

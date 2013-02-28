#!/usr/bin/python
#
# Copyright 2013, Jonas Norling <jonas.norling@gmail.com>
#

import optparse
import graph
import samples
import sys
import gtk

epilog=\
"""If no input file is specified, standard input it used. Letters in series
specifications: l=line, p=point, lp=line and point, v=vertical line for non-zero samples (event).
Colors are given as six-digit hex strings (#ff6666 is a lovely shade of pink) or as an
eight-digit string with alpha first.
"""
description=\
"Open an X window, plotting a diagram that is updated in realtime."

if __name__ == '__main__':

    # Parse command line

    parser = optparse.OptionParser(usage="Usage: %prog [options] [file]",
                                   description=description, epilog=epilog)
    parser.add_option("-x", "--x-axis", dest="x_axis", default="0:10",
                      help="X axis specification: <start>:<end> | follow", metavar="SPEC")
    parser.add_option("-y", "--y-axis", dest="y_axis", default="0:10",
                      help="Y axis specification: <start>:<end> | follow", metavar="SPEC")
    parser.add_option("-s", "--series", dest="series", default="",
                      help="Series specification: [{l|p|lp|v}[<width>]][:#<color>][:<name>],... or - to skip a series", metavar="SPEC")
    parser.add_option("-w", "--wrap", dest="wrap", default=False, action="store_true",
                      help="Wrap x axis, drawing samples in a modulo fashion")
    parser.add_option("-r", "--rate", dest="rate", default=50, type="int", metavar="N",
                      help="Set maximum update rate to N ms")

    group = optparse.OptionGroup(parser, "Sample collection options")
    group.add_option("-W", "--watch", dest="watch", default=False, action="store_true",
                     help="Watch the input file for new lines. Default for stdin")
    group.add_option("-F", "--field-separator", dest="separator", default=" ", metavar="FS",
                     help="Set the input field separator. Default is a space")
    group.add_option("-t", "--time", dest="time", default=False, action="store_true",
                     help="Use current time as X value")
    group.add_option("-c", "--count", dest="count", default=False, action="store_true",
                     help="Use sample count as X value")
    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    # Instantiate the sample collector

    if len(args) == 0:
        infile = sys.stdin
    else:
        infile = open(args[0])
    collector = samples.Collector(infile, options.separator)

    if options.time:
        collector.set_prepend_timestamp(True)
    elif options.count:
        collector.set_prepend_count(True)

    # Instantiate the graph widget

    graph_widget = graph.GraphWidget()
    try:
        graph_widget.set_axes(options.x_axis, options.y_axis)
    except:
        print "Invalid axis specification"
        exit(1)

    graph_widget.set_series(options.series)

    graph_widget.set_wrap(options.wrap)

    collector.set_graph(graph_widget)

    w = graph.MainWindow(graph_widget)
    gtk.main()

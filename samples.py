#!/usr/bin/python
#
# Copyright 2010, 2013, Jonas Norling <jonas.norling@gmail.com>
#

import gobject
import time

class Collector(object):
    def __init__(self, fd):
        self.fd = fd
        self.count = 0
        self.prepend_timestamp = False
        self.prepend_count = False
        gobject.io_add_watch(self.fd, gobject.IO_IN, self.parse_input)

    def parse_input(self, source, condition):
        line = self.fd.readline()
        items = line.split()
        values = []

        if self.prepend_timestamp:
            values.append(time.time())
        if self.prepend_count:
            values.append(self.count)
            self.count += 1

        for x in items:
            try:
                values.append(float(x))
            except ValueError:
                values.append(None)
        self.graph.draw_sample(values)
        return True

    def set_prepend_timestamp(self, v):
        self.prepend_timestamp = v

    def set_prepend_count(self, v):
        self.prepend_count = v

    def set_graph(self, g):
        self.graph = g

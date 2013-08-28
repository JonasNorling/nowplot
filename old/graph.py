#!/usr/bin/python
#
#
# Copyright 2010, 2013, Jonas Norling <jonas.norling@gmail.com>
#

import gtk
import gobject
import cairo
import math
import sys
import re

class Axis(object):
    pass

class Series(object):
    def __init__(self):
        self.linewidth = 3
        self.marker = False
        self.line = True
        self.color = (1, 1, 1, 1)
        self.label = ""

class GraphWidget(gtk.DrawingArea):
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.x_wrap = False
        self.realized = False
        self.connect("expose-event", self.on_expose_event)
        self.connect("configure-event", self.on_configure_event)
        self.connect("realize", self.on_realize)

        self.diagram_origin = (30, 20)
        self.current_sample_pos = {}

        self.backbuffer = None
        self.axisbuffer = None

    def parse_axis_spec(self, a):
        axis = Axis()
        (min, max) = a.split(":")
        axis.min = float(min)
        axis.max = float(max)
        axis.label = "Label"
        return axis

    def set_axes(self, x_axis, y_axis):
        self.x_axis = self.parse_axis_spec(x_axis)
        self.y_axis = self.parse_axis_spec(y_axis)
        self.update_axes()

    def set_series(self, s):
        self.series = []

        if s is None or s == "":
            s = "lp3"

        series_re = re.compile("([lpv]+)([0123456789]+)?(:#(.*))?(:(.*))?")
        strings = s.split(",")

        for string in strings:
            if string == "-":
                series = None
            else:
                match = series_re.match(string)
                if match is None:
                    raise ValueError
                (type, width, crap, color, crap, label) = match.groups()
                series = Series()
                if width is not None: series.linewidth = int(width)
                if type is not None: series.marker = "p" in type
                if type is not None: series.line = "l" in type
                if color is not None:
                    color = int(color, 16)
                    # Set alpha to opaque if not specified
                    if (color >> 24) & 0xff == 0: color = color | 0xff000000
                    series.color = (((color >> 16) & 0xff) / 256.0,
                                    ((color >>  8) & 0xff) / 256.0,
                                    ((color      ) & 0xff) / 256.0,
                                    ((color >> 24) & 0xff) / 256.0)
                if label is not None: series.label = label
            self.series.append(series)

    def set_wrap(self, v):
        self.x_wrap = v

    def update_axes(self):
        target_tickcount = 10.0
        tick = (self.x_axis.max - self.x_axis.min) / target_tickcount
        self.x_axis.tickdecimals = int(-math.floor(math.log10(tick)))
        self.x_axis.ticksize = round(tick, self.x_axis.tickdecimals)
        tick = (self.y_axis.max - self.y_axis.min) / target_tickcount
        self.y_axis.tickdecimals = int(-round(math.log10(tick)))
        self.y_axis.ticksize = round(tick, self.y_axis.tickdecimals)

        #print "X axis: %f .. %f, ticksize %f, tickdecimals %d" % (self.x_axis.min,
        #                                                          self.x_axis.max,
        #                                                          self.x_axis.ticksize,
        #                                                          self.x_axis.tickdecimals)

        if self.realized:
            ctx = self.bbctx
            ctx.save()
            ctx.set_source_rgb(0, 0, 0)
            ctx.paint()
            self.draw_axes()
            ctx.restore()

    def on_realize(self, widget):
        self.realized = True
        winctx = self.window.cairo_create()
        old_backbuffer = self.backbuffer
        self.backbuffer = winctx.get_target().create_similar(cairo.CONTENT_COLOR_ALPHA,
                                                             self.size[0], self.size[1])
        self.axisbuffer = winctx.get_target().create_similar(cairo.CONTENT_COLOR_ALPHA,
                                                             self.size[0], self.size[1])
        self.bbctx = cairo.Context(self.backbuffer)
        self.axctx = cairo.Context(self.axisbuffer)

        self.axctx.set_source_rgb(0, 0, 0)
        self.axctx.paint()

        # Copy and scale contents from old buffer to the new one
        if old_backbuffer is not None:
            self.bbctx.save()
            self.bbctx.scale(1.0 * self.backbuffer.get_width() / old_backbuffer.get_width(),
                             1.0 * self.backbuffer.get_height() / old_backbuffer.get_height())
            self.bbctx.set_source_surface(old_backbuffer)
            self.bbctx.paint()
            self.bbctx.restore()

        # Flip coordinate system upside-down
        self.bbctx.set_matrix(cairo.Matrix(1, 0, 0, -1, 0, self.size[1]))
        self.bbctx.translate(self.diagram_origin[0]+0.5, self.diagram_origin[1]+0.5)
        self.axctx.set_matrix(cairo.Matrix(1, 0, 0, -1, 0, self.size[1]))
        self.axctx.translate(self.diagram_origin[0]+0.5, self.diagram_origin[1]+0.5)
        self.draw_axes()

    def on_configure_event(self, widget, event):
        self.size = (event.width, event.height)
        self.diagram_size = (self.size[0] - self.diagram_origin[0] - 10,
                             self.size[1] - self.diagram_origin[1] - 10)
        self.on_realize(widget)

    def on_expose_event(self, widget, event):
        winctx = self.window.cairo_create()
        winctx.set_source_surface(self.axisbuffer)
        winctx.paint()
        winctx.set_source_surface(self.backbuffer)
        winctx.paint()

        # Highlight current sample
        if 0 in self.current_sample_pos:
            pos = self.current_sample_pos[0]
            winctx.set_matrix(cairo.Matrix(1, 0, 0, -1, 0, self.size[1]))
            winctx.translate(self.diagram_origin[0]+0.5, self.diagram_origin[1]+0.5)
            winctx.set_source_rgba(1, 0.6, 0, 1)
            winctx.arc(pos[0], pos[1], 4, 0, math.pi*2)
            winctx.fill()
            winctx.stroke()
        return True

    def fade(self):
        ctx = self.bbctx
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ATOP)
        ctx.set_source_rgba(0.2, 0.1, 0.4, 0.1)
        ctx.paint()
        ctx.restore()

    def draw_sample(self, values):
        if len(values) < 2:
            return

        ctx = self.bbctx

        x_value = values[0]
        if x_value is None:
            return

        if self.x_wrap:
            x_value = (x_value - self.x_axis.min) % (self.x_axis.max-self.x_axis.min) + self.x_axis.min
        x = (x_value - self.x_axis.min) / (self.x_axis.max-self.x_axis.min) * self.diagram_size[0]

        for ser_no in range(0, len(self.series)):
            y_value = values[ser_no + 1]

            ser = self.series[ser_no]
            if ser is None: continue
            if y_value is None: continue

            y = (y_value - self.y_axis.min) / (self.y_axis.max-self.y_axis.min) * self.diagram_size[1]

            ctx.set_source_rgba(*ser.color)
            ctx.set_line_width(ser.linewidth)
            if ser.line and \
                    ser_no in self.current_sample_pos and \
                    x >= self.current_sample_pos[ser_no][0]:
                ctx.move_to(*self.current_sample_pos[ser_no])
                ctx.line_to(x, y)
            else:
                ctx.move_to(x, y)
            if ser.marker:
                ctx.new_sub_path()
                ctx.arc(x, y, 2, 0, math.pi*2)
            ctx.stroke()
            ctx.move_to(x, y)

            self.current_sample_pos[ser_no] = (x, y)

    def draw_axes(self):
        ctx = self.axctx
        # Draw X and Y axes with arrows
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.set_line_width(1)
        ctx.move_to(self.diagram_size[0], 0)
        ctx.rel_line_to(-6, 4)
        ctx.rel_line_to(0, -4)
        ctx.rel_line_to(6, 0)
        ctx.line_to(0, 0)
        ctx.line_to(0, self.diagram_size[1])
        ctx.rel_line_to(4, -6)
        ctx.rel_line_to(-4, 0)
        ctx.stroke()

        # Draw grid and labels
        ctx.set_font_size(10)
        ctx.set_source_rgba(1, 1, 1, 0.3)

        x_tick = self.x_axis.min
        while x_tick <= self.x_axis.max:
            x = (x_tick-self.x_axis.min) * (self.diagram_size[0]/float(self.x_axis.max-self.x_axis.min))
            ctx.move_to(x, self.diagram_size[1])
            ctx.line_to(x, -5)
            ctx.stroke()

            ctx.save()
            ctx.set_source_rgba(1, 1, 1, 1)
            pattern = "%.0f"
            if self.x_axis.tickdecimals > 0:
                pattern = "%%.%df" % self.x_axis.tickdecimals
            text = pattern % x_tick
            extents = ctx.text_extents(text)
            ctx.move_to(x-extents[2]/2.0, -5-extents[3]-2)
            ctx.set_matrix(cairo.Matrix())
            ctx.show_text(text)
            ctx.stroke()
            ctx.restore()

            x_tick += self.x_axis.ticksize

        y_tick = self.y_axis.min
        while y_tick <= self.y_axis.max:
            y = (y_tick-self.y_axis.min) * (self.diagram_size[1]/float(self.y_axis.max-self.y_axis.min))
            ctx.move_to(self.diagram_size[0], y)
            ctx.line_to(-5, y)
            ctx.stroke()

            ctx.save()
            ctx.set_source_rgba(1, 1, 1, 1)
            pattern = "%.0f"
            if self.y_axis.tickdecimals > 0:
                pattern = "%%.%df" % self.y_axis.tickdecimals
            text = pattern % y_tick
            extents = ctx.text_extents(text)
            ctx.move_to(-5-extents[2]-3, y-extents[3]/2.0)
            ctx.set_matrix(cairo.Matrix())
            ctx.show_text(text)
            ctx.stroke()
            ctx.restore()

            y_tick += self.y_axis.ticksize

        # Draw axis labels
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.save()
        text = self.x_axis.label
        extents = ctx.text_extents(text)
        ctx.move_to(self.diagram_size[0]-extents[2], -extents[3]-2)
        ctx.set_matrix(cairo.Matrix())
        ctx.show_text(text)
        ctx.restore()

        ctx.save()
        text = self.y_axis.label
        extents = ctx.text_extents(text)
        ctx.move_to(-extents[2]-3, self.diagram_size[1]-extents[3])
        ctx.set_matrix(cairo.Matrix())
        ctx.show_text(text)
        ctx.restore()
        ctx.stroke()


class MainWindow(gtk.Window):
    def __init__(self, graph_widget):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_default_size(800, 480);
        self.connect("destroy", self.quit_callback)

        main_box = gtk.HBox()
        self.add(main_box)
        self.graph = graph_widget
        main_box.pack_start(self.graph, True)

        gobject.timeout_add(50, lambda: self.graph.queue_draw() or True)
        #gobject.timeout_add(500, lambda: self.graph.fade() or True)
        self.show_all()

    def quit_callback(self, b):
        gtk.main_quit()

import cairo

class OverlayPlotter(object):
    def __init__(self, surface, size, xAxis, yAxis):
        self.surface = surface
        self.size = size
        
        self.xAxis = xAxis
        self.yAxis = yAxis
                
        self.ctx = cairo.Context(self.surface)
        
        # Flip coordinate system upside-down
        self.ctx.set_matrix(cairo.Matrix(1, 0, 0, -1, 0, self.size[1]))
        
        self.axiscolor = (0, 0, 0, 0.5)
        self.gridcolor = (0, 0, 0, 0.1)
        self.textcolor = (1, 1, 1, 0.7)
        
    def setXAxis(self, xAxis):
        self.xAxis = xAxis

    def setYAxis(self, yAxis):
        self.yAxis = yAxis
    
    def draw(self):
        ctx = self.ctx
        ctx.set_source_rgba(0, 0, 0, 0)
        ctx.paint()

        # Draw axes
        
        ctx.set_source_rgba(*self.axiscolor)
        ctx.set_line_width(2)

        zeroy = self.yAxis.map(0.0) * self.size[1]
        ctx.move_to(0, zeroy)
        ctx.line_to(self.size[0], zeroy)
        ctx.stroke()

        zerox = self.xAxis.map(0.0) * self.size[0]
        ctx.move_to(zerox, 0)
        ctx.line_to(zerox, self.size[1])
        ctx.stroke()
        
        # Draw grid and labels
        
        ctx.set_source_rgba(*self.gridcolor)
        ctx.set_font_size(10)
        
        x_tick = round(self.xAxis.min, self.xAxis.tickdecimals)
        while x_tick <= self.xAxis.max:
            x = (x_tick - self.xAxis.min) * (self.size[0] / float(self.xAxis.max - self.xAxis.min))
            ctx.move_to(x, self.size[1])
            ctx.line_to(x, 0)
            ctx.stroke()

            ctx.save()
            ctx.set_source_rgba(*self.textcolor)
            pattern = "%.0f"
            if self.xAxis.tickdecimals > 0:
                pattern = "%%.%df" % self.xAxis.tickdecimals
            text = pattern % x_tick
            extents = ctx.text_extents(text)
            if zeroy > 50:
                ctx.move_to(x - extents[2] / 2.0, zeroy - extents[3] - 2)
            else:
                ctx.move_to(x - extents[2] / 2.0, 3)
            ctx.set_matrix(cairo.Matrix())
            ctx.show_text(text)
            ctx.stroke()
            ctx.restore()

            x_tick += self.xAxis.ticksize
    
        y_tick = round(self.yAxis.min, self.yAxis.tickdecimals)
        while y_tick <= self.yAxis.max:
            y = (y_tick - self.yAxis.min) * (self.size[1] / float(self.yAxis.max - self.yAxis.min))
            ctx.move_to(self.size[0], y)
            ctx.line_to(0, y)
            ctx.stroke()

            ctx.save()
            ctx.set_source_rgba(*self.textcolor)
            pattern = "%.0f"
            if self.yAxis.tickdecimals > 0:
                pattern = "%%.%df" % self.yAxis.tickdecimals
            text = pattern % y_tick
            extents = ctx.text_extents(text)
            if zerox > 50:
                ctx.move_to(zerox -5 - extents[2] - 3, y - extents[3] / 2.0)
            else:
                ctx.move_to(3, y - extents[3] / 2.0)
            ctx.set_matrix(cairo.Matrix())
            ctx.show_text(text)
            ctx.stroke()
            ctx.restore()

            y_tick += self.yAxis.ticksize
            
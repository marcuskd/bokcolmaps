"""SpotPlot class definition"""

import numpy

from bokeh.plotting import Figure

from bokeh.models import ColumnDataSource, Plot, ColorBar
from bokeh.models.mappers import LinearColorMapper
from bokeh.models.layouts import Column

from bokeh.core.properties import Instance, String, Int, Float, Bool

from bokcolmaps.get_common_kwargs import get_common_kwargs
from bokcolmaps.generate_colourbar import generate_colourbar
from bokcolmaps.read_colourmap import read_colourmap
from bokcolmaps.get_min_max import get_min_max


class SpotPlot(Column):

    """
    Like a scatter plot but with the points colour mapped with a
    user-defined colour scale.
    """

    __view_model__ = 'Column'
    __subtype__ = 'SpotPlot'

    __view_module__ = 'bokeh'

    __sizing_mode__ = 'stretch_both'

    plot = Instance(Plot)
    cbar = Instance(ColorBar)

    datasrc = Instance(ColumnDataSource)
    coldatasrc = Instance(ColumnDataSource)
    cvals = Instance(ColumnDataSource)
    cmap = Instance(LinearColorMapper)

    title_root = String
    zlab = String
    bg_col = String
    nan_col = String
    sp_size = Int
    rmin = Float
    rmax = Float
    autoscale = Bool
    cbdelta = Float

    def __init__(self, x, y, z, dm, **kwargs):

        """
        args...
            x: 1D NumPy array of x coordinates for the spot locations
            y: 1D NumPy array of y coordinates for the spot locations, same size as x
            z: 1D NumPy array of (common) z coordinates
            dm: 2D NumPy array of the data for display, dimensions z.size by x.size
        kwargs: all in get_common_kwargs plus...
            height: plot height (pixels)
            width: plot width (pixels)
        """

        palette, cfile, revcols, xlab, ylab, zlab, dmlab, \
            rmin, rmax, xran, yran, alpha, nan_colour = get_common_kwargs(**kwargs)

        height = kwargs.get('height', 575)
        width = kwargs.get('width', 500)

        super().__init__()

        self.cbdelta = 0.01  # Min colourbar range (used if values are equal)

        self.title_root = dmlab
        self.zlab = zlab

        self.rmin = rmin
        self.rmax = rmax
        self.autoscale = True
        if (self.rmin is not None) & (self.rmax is not None):
            self.autoscale = False

        if z.size > 1:  # Default to first 'slice'
            d = dm[0]
        else:
            d = dm

        if self.autoscale:
            min_val, max_val = get_min_max(d, self.cbdelta)
        else:
            min_val = self.rmin
            max_val = self.rmax

        if cfile is not None:
            self.read_cmap(cfile)
            palette = self.cvals.data['colours']
            if revcols:
                self.cvals.data['colours'].reverse()

        self.cmap = LinearColorMapper(palette=palette, nan_color=nan_colour)

        if revcols and (cfile is None):
            pal = list(self.cmap.palette)
            pal.reverse()
            self.cmap.palette = tuple(pal)

        self.cmap.low = min_val
        self.cmap.high = max_val

        if cfile is None:
            self.cvals = ColumnDataSource(data={'colours': self.cmap.palette})

        self.bg_col = 'black'
        self.nan_col = nan_colour
        self.sp_size = int(min(height, width) / 40)

        cols = [self.nan_col] * d.size  # Initially empty
        self.datasrc = ColumnDataSource(data={'z': [z], 'd': [d], 'dm': [dm]})
        self.coldatasrc = ColumnDataSource(data={'x': x, 'y': y, 'cols': cols})

        ptools = ['reset, pan, wheel_zoom, box_zoom, save']

        # Default to entire range unless externally controlled
        if xran is None:
            xran = [x.min(), x.max()]
        if yran is None:
            yran = [y.min(), y.max()]

        self.plot = Figure(x_axis_label=xlab, y_axis_label=ylab,
                           x_range=xran, y_range=yran,
                           plot_height=height, plot_width=width,
                           background_fill_color=self.bg_col,
                           tools=ptools, toolbar_location='right')

        self.plot.circle('x', 'y', size=self.sp_size, color='cols',
                         source=self.coldatasrc,
                         nonselection_fill_color='cols',
                         selection_fill_color='cols',
                         fill_alpha=alpha, line_alpha=alpha,
                         nonselection_fill_alpha=alpha, selection_fill_alpha=alpha,
                         nonselection_line_alpha=0, selection_line_alpha=alpha,
                         nonselection_line_color='cols',
                         selection_line_color='white', line_width=5)

        self.update_title(0)

        self.plot.title.text_font = 'garamond'
        self.plot.title.text_font_size = '12pt'
        self.plot.title.text_font_style = 'bold'
        self.plot.title.align = 'center'

        self.plot.xaxis.axis_label_text_font = 'garamond'
        self.plot.xaxis.axis_label_text_font_size = '10pt'
        self.plot.xaxis.axis_label_text_font_style = 'bold'

        self.plot.yaxis.axis_label_text_font = 'garamond'
        self.plot.yaxis.axis_label_text_font_size = '10pt'
        self.plot.yaxis.axis_label_text_font_style = 'bold'

        self.update_colours()

        self.cbar = generate_colourbar(self.cmap, cbarwidth=round(height / 20))
        self.plot.add_layout(self.cbar, 'below')

        self.children.append(self.plot)

    def read_cmap(self, fname):

        """
        Read in the colour scale
        """

        self.cvals = read_colourmap(fname)

    def changed(self, zind):

        """
        Change the row of dm being displayed
        (i.e. a different value of z)
        """

        if (len(self.datasrc.data['dm'][0].shape) > 1) and \
           (zind >= 0) and (zind < self.datasrc.data['dm'][0].shape[0]):

            data = self.datasrc.data
            newdata = data
            d = data['dm'][0][zind]
            newdata['d'] = [d]

            self.datasrc.trigger('data', data, newdata)

    def update_cbar(self):

        """
        Update the colour scale (needed when the data for display changes)
        """

        if self.autoscale:

            d = self.datasrc.data['d'][0]
            min_val, max_val = get_min_max(d, self.cbdelta)

            self.cmap.low = min_val
            self.cmap.high = max_val

    def update_colours(self):

        """
        Update the spot colours (needed when the data for display changes)
        """

        colset = self.cvals.data['colours']
        ncols = len(colset)

        d = self.datasrc.data['d'][0]

        data = self.coldatasrc.data
        newdata = data
        cols = data['cols']

        min_val = self.cmap.low
        max_val = self.cmap.high

        for s in range(d.size):

            if numpy.isfinite(d[s]):

                cind = int(round(ncols * (d[s] - min_val) / (max_val - min_val)))
                if cind < 0:
                    cind = 0
                if cind >= ncols:
                    cind = ncols - 1

                cols[s] = colset[cind]

            else:

                cols[s] = self.nan_col

        newdata['cols'] = cols

        self.coldatasrc.trigger('data', data, newdata)

    def update_title(self, zind):

        """
        Update the plot title (needed when the z index changes)
        """

        if self.datasrc.data['z'][0].size > 1:
            self.plot.title.text = self.title_root + ', ' + \
                self.zlab + ' = ' + str(self.datasrc.data['z'][0][zind])
        else:
            self.plot.title.text = self.title_root

    def input_change(self, attrname, old, new):

        """
        Callback for use with e.g. sliders
        """

        self.changed(new)
        self.update_cbar()
        self.update_colours()
        self.update_title(new)

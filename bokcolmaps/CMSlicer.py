"""
CMSlicer class definition
"""

import numpy

from bokeh.models.sources import ColumnDataSource
from bokeh.layouts import Row
from bokeh.core.properties import Instance, Bool
from bokeh.models.renderers import GlyphRenderer
from bokeh.models.glyphs import Line

from bokcolmaps.get_common_kwargs import get_common_kwargs


class CMSlicer(Row):

    """
    Base class for CMSlicer2D and CMSlicer3D.
    """

    __view_model__ = 'Row'
    __subtype__ = 'CMSlicer'

    __view_module__ = 'bokeh'

    nu_tol_default = 1.

    sl_src = Instance(ColumnDataSource)
    cmap_params = Instance(ColumnDataSource)
    lr = Instance(GlyphRenderer)

    is_selecting = Bool

    def __init__(self, x, y, **kwargs):

        """
        All init arguments same as for ColourMapLPSlider
        """

        super().__init__()

        palette, cfile, revcols, xlab, ylab, zlab, dmlab, \
            rmin, rmax, xran, yran, alpha, nan_colour = get_common_kwargs(**kwargs)

        cmheight = kwargs.get('cmheight', 575)
        cmwidth = kwargs.get('cmwidth', 500)
        lpwidth = kwargs.get('lpwidth', 300)
        revz = kwargs.get('revz', False)
        hoverdisp = kwargs.get('hoverdisp', True)

        self.height = cmheight
        self.width = int((2 * cmwidth + lpwidth) * 1.1)

        x0, x1 = x[0], x[-1]
        ymean = (y[0] + y[-1]) / 2
        y0, y1 = ymean, ymean
        self.sl_src = ColumnDataSource(data={'x': [x0, x1], 'y': [y0, y1]})

        self.cmap_params = ColumnDataSource(data={'palette': [palette],
                                                  'cfile': [cfile],
                                                  'revcols': [revcols],
                                                  'xlab': [xlab],
                                                  'ylab': [ylab],
                                                  'zlab': [zlab],
                                                  'dmlab': [dmlab],
                                                  'rmin': [rmin],
                                                  'rmax': [rmax],
                                                  'xran': [xran],
                                                  'yran': [yran],
                                                  'alpha': [alpha],
                                                  'nan_colour': [nan_colour],
                                                  'cmheight': [cmheight],
                                                  'cmwidth': [cmwidth]})

        self.is_selecting = False

    def get_interp_coords(self, datasrc):

        """
        Get the interpolation coordinates and range values
        """

        x = datasrc.data['x'][0]
        y = datasrc.data['y'][0]

        dx = numpy.min(numpy.abs(numpy.diff(x)))
        dy = numpy.min(numpy.abs(numpy.diff(y)))

        x0, x1 = self.sl_src.data['x'][0], self.sl_src.data['x'][1]
        y0, y1 = self.sl_src.data['y'][0], self.sl_src.data['y'][1]

        nx = int(numpy.floor(numpy.abs(x1 - x0) / dx)) + 1
        ny = int(numpy.floor(numpy.abs(y1 - y0) / dy)) + 1
        nc = numpy.max([nx, ny])

        x_i = numpy.linspace(x0, x1, nc)
        y_i = numpy.linspace(y0, y1, nc)
        c_i = numpy.array(list(zip(y_i, x_i)))

        r_i = numpy.sqrt((x_i - x_i[0]) ** 2 + (y_i - y_i[0]) ** 2)

        return c_i, r_i

    def change_slice(self):

        """
        Empty here as subclass-specific
        """

        pass

    def toggle_select(self, event):

        """
        Handle Tap events for slice change
        """

        if self.is_selecting:

            self.is_selecting = False
            self.sl_src.data['x'][1] = event.x
            self.sl_src.data['y'][1] = event.y

            self.cmap.renderers.remove(self.lr)
            self.lr = self.cmap.add_glyph(self.sl_src, glyph=Line(x='x', y='y', line_color='white', line_width=5,
                                                                  line_dash='dashed', line_alpha=1))

            self.change_slice()

        else:

            self.is_selecting = True
            self.sl_src.data['x'][0] = event.x
            self.sl_src.data['y'][0] = event.y

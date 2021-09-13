"""
CMSlicer3D class definition
"""

import numpy

from bokeh.core.properties import Instance, Bool
from bokeh.models.sources import ColumnDataSource
from bokeh.models.renderers import GlyphRenderer
from bokeh.models.widgets import Div
from bokeh.models.glyphs import Line
from bokeh.plotting import Figure
from bokeh.events import Tap
from bokeh.layouts import Row, Column

from bokcolmaps.ColourMap import ColourMap
from bokcolmaps.ColourMapLPSlider import ColourMapLPSlider

from bokcolmaps.get_common_kwargs import get_common_kwargs
from bokcolmaps.interp_2d_line import interp_2d_line


class CMSlicer3D(Row):

    """
    A ColourMapLPSlider with the ability to slice the plot with a line through the x-y plane which gives the
    profile against z along the line as a separate ColourMap.
    """

    __view_model__ = 'Row'
    __subtype__ = 'CMSlicer3D'

    __view_module__ = 'bokeh'

    nu_tol_default = 1.

    cmap = Instance(ColourMapLPSlider)
    sl_src = Instance(ColumnDataSource)
    cmap_params = Instance(ColumnDataSource)
    lr = Instance(GlyphRenderer)

    is_selecting = Bool

    def __init__(self, x, y, z, dm, **kwargs):

        """
        All init arguments same as for ColourMapLPSlider.
        """

        super().__init__()

        palette, cfile, revcols, xlab, ylab, zlab, dmlab, \
            rmin, rmax, xran, yran, alpha, nan_colour = get_common_kwargs(**kwargs)

        cmheight = kwargs.get('cmheight', 575)
        cmwidth = kwargs.get('cmwidth', 500)
        lpheight = kwargs.get('lpheight', 500)
        lpwidth = kwargs.get('lpwidth', 300)
        revz = kwargs.get('revz', False)
        hoverdisp = kwargs.get('hoverdisp', True)

        self.height = cmheight
        self.width = int((2 * cmwidth + lpwidth) * 1.1)

        self.cmap = ColourMapLPSlider(x, y, z, dm, palette=palette, cfile=cfile, revcols=revcols,
                                      xlab=xlab, ylab=ylab, zlab=zlab, dmlab=dmlab,
                                      cmheight=cmheight, cmwidth=cmwidth, lpheight=lpheight, lpwidth=lpwidth,
                                      rmin=rmin, rmax=rmax, xran=xran, yran=yran, alpha=alpha, nan_colour=nan_colour,
                                      revz=revz, hoverdisp=hoverdisp, scbutton=True)

        self.cmap.cmaplp.cmplot.plot.on_event(Tap, self.toggle_select)

        x0, x1 = x[0], x[-1]
        ymean = (y[0] + y[-1]) / 2
        y0, y1 = ymean, ymean
        self.sl_src = ColumnDataSource(data={'x': [x0, x1], 'y': [y0, y1]})
        self.lr = self.cmap.cmaplp.cmplot.plot.add_glyph(self.sl_src, glyph=Line(x='x', y='y', line_color='white',
                                                         line_width=5, line_dash='dashed', line_alpha=1))

        self.children.append(self.cmap)

        self.children.append(Column(children=[Div(text='', width=cmwidth, height=35), Figure(toolbar_location=None)]))

        self.cmap_params = ColumnDataSource(data={'palette': [palette],
                                                  'cfile': [cfile],
                                                  'revcols': [revcols],
                                                  'zlab': [zlab],
                                                  'dmlab': [dmlab],
                                                  'cmheight': [cmheight],
                                                  'cmwidth': [cmwidth],
                                                  'rmin': [rmin],
                                                  'rmax': [rmax],
                                                  'alpha': [alpha],
                                                  'nan_colour': [nan_colour],
                                                  'revz': [revz]})

        self.change_slice()

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
        Change the slice displayed in the separate line plot
        """

        c_i, r_i = self.get_interp_coords(self.cmap.cmaplp.cmplot.datasrc)

        x = self.cmap.cmaplp.cmplot.datasrc.data['x'][0]
        y = self.cmap.cmaplp.cmplot.datasrc.data['y'][0]
        z = self.cmap.cmaplp.cmplot.datasrc.data['z'][0]

        dm = self.cmap.cmaplp.cmplot.datasrc.data['dm'][0]
        dm = numpy.reshape(dm, [z.size, y.size, x.size])

        dm_i, z_i = interp_2d_line(y, x, dm, c_i, z=z)

        if self.cmap_params.data['revz'][0]:
            z_i = numpy.flipud(z_i)
            dm_i = numpy.flipud(dm_i)

        iplot = ColourMap(r_i, z_i, [0], dm_i, palette=self.cmap_params.data['palette'][0],
                          cfile=self.cmap_params.data['cfile'][0], revcols=self.cmap_params.data['revcols'][0],
                          xlab='Units', ylab=self.cmap_params.data['zlab'][0], dmlab=self.cmap_params.data['dmlab'][0],
                          height=self.cmap_params.data['cmheight'][0], width=self.cmap_params.data['cmwidth'][0],
                          rmin=self.cmap_params.data['rmin'][0], rmax=self.cmap_params.data['rmax'][0],
                          alpha=self.cmap_params.data['alpha'][0], nan_colour=self.cmap_params.data['nan_colour'][0])

        self.children[1].children[1] = iplot

    def toggle_select(self, event):

        """
        Handle Tap events for slice change
        """

        if self.is_selecting:

            self.is_selecting = False
            self.sl_src.data['x'][1] = event.x
            self.sl_src.data['y'][1] = event.y

            self.cmap.cmaplp.cmplot.plot.renderers.remove(self.lr)
            self.lr = self.cmap.cmaplp.cmplot.plot.add_glyph(self.sl_src, glyph=Line(x='x', y='y', line_color='white',
                                                                                     line_width=5, line_dash='dashed',
                                                                                     line_alpha=1))

            self.change_slice()

        else:

            self.is_selecting = True
            self.sl_src.data['x'][0] = event.x
            self.sl_src.data['y'][0] = event.y

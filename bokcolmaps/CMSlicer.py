'''CMSlicer class definition'''

import numpy

from bokeh.models.sources import ColumnDataSource
from bokeh.layouts import Column, Row
from bokeh.models.widgets import Div
from bokeh.events import Tap
from bokeh.core.properties import Instance, Float, Bool
from bokeh.plotting import Figure
from bokeh.models.renderers import GlyphRenderer

from .ColourMapLPSlider import ColourMapLPSlider
from .ColourMap import ColourMap

from .get_common_kwargs import get_common_kwargs
from .interp_2d_line import interp_2d_line


class CMSlicer(Row):

    nu_tol_default = 1.

    '''
    A ColourMapLPSlider with the ability to slice the plot with a line
    through the x-y plane which gives the profile against z along the line
    as a separate ColourMap.
    '''

    __view_model__ = "Row"
    __subtype__ = "CMSlicer"

    cmap_lps = Instance(ColourMapLPSlider)
    cmap = Instance(ColourMap)
    cm_src = Instance(ColumnDataSource)
    sl_src = Instance(ColumnDataSource)
    cmap_params = Instance(ColumnDataSource)
    lr = Instance(GlyphRenderer)

    xstart = Float
    xend = Float
    ystart = Float
    yend = Float
    is_selecting = Bool

    def __init__(self, x, y, z, dm, **kwargs):

        '''
        All init arguments same as for ColourMapLPSlider.
        '''

        palette, cfile, xlab, ylab, zlab,\
            dmlab, rmin, rmax, xran, yran = get_common_kwargs(**kwargs)

        cmheight = kwargs.get('cmheight', 575)
        cmwidth = kwargs.get('cmwidth', 500)
        lpheight = kwargs.get('lpheight', 500)
        lpwidth = kwargs.get('lpwidth', 300)
        revz = kwargs.get('revz', False)
        hoverdisp = kwargs.get('hoverdisp', True)

        super().__init__()

        self.height = cmheight
        self.width = int((2*cmwidth + lpwidth)*1.1)

        self.cmap_lps = ColourMapLPSlider(x, y, z, dm, palette=palette,
                                          cfile=cfile, xlab=xlab, ylab=ylab,
                                          zlab=zlab, dmlab=dmlab,
                                          cmheight=cmheight, cmwidth=cmwidth,
                                          lpheight=lpheight, lpwidth=lpwidth,
                                          rmin=rmin, rmax=rmax, xran=xran,
                                          yran=yran, revz=revz,
                                          hoverdisp=hoverdisp)

        cmap = self.cmap_lps.cmaplp.cmplot.plot
        cmap.on_event(Tap, self.toggle_select)

        x0, x1 = x[0], x[-1]
        ymean = (y[0] + y[-1])/2
        y0, y1 = ymean, ymean
        self.sl_src = ColumnDataSource(data={'x': [x0, x1], 'y': [y0, y1]})

        self.lr = cmap.line('x', 'y', source=self.sl_src, line_color='white',
                            line_width=5, line_dash='dashed', line_alpha=0.8)

        self.children.append(self.cmap_lps)
        self.children.append(Column(children=[Div(text='', width=cmwidth,
                                                  height=35),
                                              Figure(toolbar_location=None)]))

        self.cmap_params = ColumnDataSource(data={'palette': [palette],
                                                  'cfile': [cfile],
                                                  'zlab': [zlab],
                                                  'dmlab': [dmlab],
                                                  'cmheight': [cmheight],
                                                  'cmwidth': [cmwidth],
                                                  'rmin': [rmin],
                                                  'rmax': [rmax],
                                                  'xran': [xran],
                                                  'yran': [yran]})
        self.change_slice()

        self.is_selecting = False

    def change_slice(self):

        datasrc = self.cmap_lps.cmaplp.cmplot.datasrc
        x = datasrc.data['x'][0]
        y = datasrc.data['y'][0]
        z = datasrc.data['z'][0]
        dm = datasrc.data['dm'][0].copy()
        dm = numpy.reshape(dm, [z.size, y.size, x.size])

        dx = numpy.min(numpy.abs(numpy.diff(x)))
        dy = numpy.min(numpy.abs(numpy.diff(y)))

        x0, x1 = self.sl_src.data['x'][0], self.sl_src.data['x'][1]
        y0, y1 = self.sl_src.data['y'][0], self.sl_src.data['y'][1]

        nx = int(numpy.floor(numpy.abs(x1 - x0)/dx)) + 1
        ny = int(numpy.floor(numpy.abs(y1 - y0)/dy)) + 1
        nc = numpy.max([nx, ny])

        x_i = numpy.linspace(x0, x1, nc)
        y_i = numpy.linspace(y0, y1, nc)
        c_i = numpy.array(list(zip(y_i, x_i)))

        dm_i, z_i = interp_2d_line(y, x, dm, c_i, z=z)

        r_i = numpy.sqrt((x_i - x_i[0])**2 + (y_i - y_i[0])**2)

        cmap = ColourMap(r_i, z_i, [0], dm_i,
                         palette=self.cmap_params.data['palette'][0],
                         cfile=self.cmap_params.data['cfile'][0],
                         xlab=' ', ylab=self.cmap_params.data['zlab'][0],
                         dmlab=self.cmap_params.data['dmlab'][0],
                         height=self.cmap_params.data['cmheight'][0],
                         width=self.cmap_params.data['cmwidth'][0],
                         rmin=self.cmap_params.data['rmin'][0],
                         rmax=self.cmap_params.data['rmax'][0],
                         xran=self.cmap_params.data['xran'][0],
                         yran=self.cmap_params.data['yran'][0])
        self.children[1].children[1] = cmap

    def toggle_select(self, event):

        if self.is_selecting:

            self.is_selecting = False
            self.sl_src.data['x'][1] = event.x
            self.sl_src.data['y'][1] = event.y
            self.cmap_lps.cmaplp.cmplot.plot.renderers.remove(self.lr)
            self.cmap_lps.cmaplp.cmplot.plot.renderers.append(self.lr)
            self.change_slice()

        else:

            self.is_selecting = True
            self.sl_src.data['x'][0] = event.x
            self.sl_src.data['y'][0] = event.y

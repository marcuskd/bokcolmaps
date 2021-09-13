"""
CMSlicer2D class definition
"""

import numpy

from bokeh.layouts import Column
from bokeh.models.widgets import Div
from bokeh.events import Tap
from bokeh.core.properties import Instance
from bokeh.plotting import Figure
from bokeh.models.glyphs import Line

from bokcolmaps.CMSlicer import CMSlicer
from bokcolmaps.ColourMap import ColourMap

from bokcolmaps.interp_2d_line import interp_2d_line


class CMSlicer2D(CMSlicer):

    """
    A ColourMap with the ability to slice the plot with a line through the x-y plane to give a separate line plot.
    """

    __view_model__ = CMSlicer.__view_model__
    __subtype__ = 'CMSlicer2D'

    cmap = Instance(ColourMap)

    def __init__(self, x, y, z, dm, **kwargs):

        """
        All init arguments same as for ColourMapLPSlider.
        """

        super().__init__(x, y, **kwargs)

        params = self.cmap_params.data
        self.cmap = ColourMap(x, y, z, dm, palette=params['palette'][0], cfile=params['cfile'][0],
                              revcols=params['revcols'][0], xlab=params['xlab'][0],
                              ylab=params['ylab'][0], zlab=params['zlab'][0], dmlab=params['dmlab'][0],
                              height=params['cmheight'][0], width=params['cmwidth'][0],
                              rmin=params['rmin'][0], rmax=params['rmax'][0],
                              xran=params['xran'][0], yran=params['yran'][0],
                              alpha=params['alpha'][0], nan_colour=params['nan_colour'][0])

        self.cmap.plot.on_event(Tap, self.toggle_select)

        self.lr = self.cmap.plot.add_glyph(self.sl_src, glyph=Line(x='x', y='y', line_color='white',
                                           line_width=5, line_dash='dashed', line_alpha=1))

        self.children.append(self.cmap)

        self.children.append(Column(children=[Div(text='', width=params['cmwidth'][0], height=0),
                                              Figure(toolbar_location=None)]))

        self.change_slice()

    def change_slice(self):

        """
        Change the slice displayed in the separate ColourMap
        """

        c_i, r_i = self.get_interp_coords(self.cmap.datasrc)

        x = self.cmap.datasrc.data['x'][0]
        y = self.cmap.datasrc.data['y'][0]

        dm = self.cmap.datasrc.data['dm'][0]
        dm = numpy.reshape(dm, [y.size, x.size])

        dm_i, z_i = interp_2d_line(y, x, dm, c_i)

        iplot = Figure(x_axis_label='Units', y_axis_label=self.cmap_params.data['zlab'][0],
                       plot_height=self.cmap_params.data['cmheight'][0], plot_width=self.cmap_params.data['cmwidth'][0],
                       x_range=[r_i[0], r_i[-1]], toolbar_location='right')

        iplot.line(r_i, dm_i, line_color='blue', line_width=2, line_alpha=1)

        self.children[1].children[1] = iplot

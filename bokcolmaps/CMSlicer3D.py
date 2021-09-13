"""
CMSlicer3D class definition
"""

import numpy

from bokeh.layouts import Column
from bokeh.models.widgets import Div
from bokeh.events import Tap
from bokeh.core.properties import Instance
from bokeh.plotting import Figure
from bokeh.models.glyphs import Line

from bokcolmaps.CMSlicer import CMSlicer
from bokcolmaps.ColourMapLPSlider import ColourMapLPSlider
from bokcolmaps.ColourMap import ColourMap

from bokcolmaps.interp_2d_line import interp_2d_line


class CMSlicer3D(CMSlicer):

    """
    A ColourMapLPSlider with the ability to slice the plot with a line through the x-y plane which gives the
    profile against z along the line as a separate ColourMap.
    """

    __view_model__ = CMSlicer.__view_model__
    __subtype__ = 'CMSlicer3D'

    cmap = Instance(ColourMapLPSlider)

    def __init__(self, x, y, z, dm, **kwargs):

        """
        All init arguments same as for ColourMapLPSlider.
        """

        super().__init__(x, y, **kwargs)

        params = self.cmap_params.data

        params['lpheight'] = [kwargs.get('lpheight', 500)]
        params['lpwidth'] = [kwargs.get('lpwidth', 300)]
        params['revz'] = [kwargs.get('revz', False)]
        params['hoverdisp'] = [kwargs.get('hoverdisp', True)]

        self.cmap = ColourMapLPSlider(x, y, z, dm, palette=params['palette'][0], cfile=params['cfile'][0],
                                      revcols=params['revcols'][0], xlab=params['xlab'][0],
                                      ylab=params['ylab'][0], zlab=params['zlab'][0], dmlab=params['dmlab'][0],
                                      cmheight=params['cmheight'][0], cmwidth=params['cmwidth'][0],
                                      lpheight=params['lpheight'][0], lpwidth=params['lpwidth'][0],
                                      rmin=params['rmin'][0], rmax=params['rmax'][0],
                                      xran=params['xran'][0], yran=params['yran'][0],
                                      revz=params['revz'][0], hoverdisp=params['hoverdisp'][0], scbutton=True,
                                      alpha=params['alpha'][0], nan_colour=params['nan_colour'][0])

        self.cmap.cmaplp.cmplot.plot.on_event(Tap, self.toggle_select)

        self.lr = self.cmap.cmaplp.cmplot.plot.add_glyph(self.sl_src, glyph=Line(x='x', y='y', line_color='white',
                                                         line_width=5, line_dash='dashed', line_alpha=1))

        self.children.append(self.cmap)

        self.children.append(Column(children=[Div(text='', width=params['cmwidth'][0], height=35),
                                              Figure(toolbar_location=None)]))

        self.change_slice()

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
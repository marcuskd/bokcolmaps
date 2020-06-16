"""
ColourMap3Slider class definition
"""

from bokeh.models.widgets import Slider
from bokeh.models.layouts import Column

from bokeh.core.properties import Instance

from bokcolmaps.ColourMap3 import ColourMap3

from bokcolmaps.get_common_kwargs import get_common_kwargs


class ColourMap3Slider(Column):

    """
    A ColourMap3 with a slider linked to the z coordinate
    (i.e. the 2D slice being displayed).
    """

    __view_model__ = 'Column'
    __subtype__ = 'ColourMap3Slider'

    __view_module__ = 'bokeh'

    cmap = Instance(ColourMap3)
    zslider = Instance(Slider)

    def __init__(self, x, y, z, dm, **kwargs):

        """
        All init arguments same as for ColourMap3.
        """

        palette, cfile, revcols, xlab, ylab, zlab,\
            dmlab, rmin, rmax, xran, yran = get_common_kwargs(**kwargs)

        height = kwargs.get('height', 575)
        width = kwargs.get('width', 500)
        hover = kwargs.get('hover', True)

        super().__init__()

        self.height = height
        self.width = int(width * 1.1)

        self.cmap = ColourMap3(x, y, z, dm,
                               palette=palette, cfile=cfile, revcols=revcols,
                               xlab=xlab, ylab=ylab, zlab=zlab, dmlab=dmlab,
                               height=height, width=width, rmin=rmin, rmax=rmax,
                               xran=xran, yran=yran, hover=hover)

        self.zslider = Slider(title=zlab + ' index', start=0, end=z.size - 1,
                              step=1, value=0, orientation='horizontal')

        self.zslider.js_on_change('value', self.cmap.cjs_slider)

        self.children.append(Column(self.zslider, width=self.width))
        self.children.append(self.cmap)

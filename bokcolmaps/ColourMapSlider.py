'''ColourMapSlider class definition'''

from bokeh.models.widgets import Slider
from bokeh.models.layouts import Column, WidgetBox

from bokeh.core.properties import Instance

from .ColourMap import ColourMap


class ColourMapSlider(Column):

    '''
    A ColourMap with a slider linked to the z coordinate
    (i.e. the 2D slice being displayed).
    '''

    __view_model__ = "Column"
    __subtype__ = "ColourMapSlider"

    cmap = Instance(ColourMap)
    zslider = Instance(Slider)

    def __init__(self, x, y, z, D, palette='Viridis256', cfile='jet.txt',
                 xlab='x', ylab='y', zlab='Index', Dlab='Data',
                 height=575, width=500, rmin=None, rmax=None,
                 xran=None, yran=None, hover=True):

        '''
        All init arguments same as for ColourMap.
        '''

        super().__init__()

        self.height = height
        self.width = int(width*1.1)

        self.cmap = ColourMap(x, y, z, D, palette=palette, cfile=cfile,
                              xlab=xlab, ylab=ylab, zlab=zlab, Dlab=Dlab,
                              height=height, width=width, rmin=rmin, rmax=rmax,
                              xran=xran, yran=yran, hover=hover)

        self.zslider = Slider(title='z index', start=0, end=z.size-1, step=1,
                              value=0, orientation='horizontal')

        self.zslider.on_change('value', self.cmap.input_change)

        self.children.append(WidgetBox(self.zslider, width=self.width))
        self.children.append(self.cmap)

'''SplotPlotLPSlider class definition'''

from bokeh.models.widgets import Slider
from bokeh.models.layouts import Column, WidgetBox

from bokeh.core.properties import Instance

from .SpotPlotLP import SpotPlotLP


class SpotPlotLPSlider(Column):

    '''
    A SpotPlotLP with a slider linked to the z coordinate
    (i.e. the row being displayed).
    '''

    __view_model__ = "Column"
    __subtype__ = "SpotPlotLPSlider"

    splotlp = Instance(SpotPlotLP)
    zslider = Instance(Slider)

    def __init__(self, x, y, z, D, palette='Viridis256', cfile='jet.txt',
                 xlab='x', ylab='y', zlab='Index', Dlab='Data',
                 spheight=575, spwidth=500, lpheight=500, lpwidth=300,
                 rmin=None, rmax=None, xran=None, yran=None, revz=False):

        '''
        All init arguments same as for SpotPlotLP.
        '''

        super(SpotPlotLPSlider, self).__init__()

        self.height = spheight
        self.width = int((spwidth + lpwidth)*1.1)

        self.splotlp = SpotPlotLP(x, y, z, D, palette=palette, cfile=cfile,
                                  xlab=xlab, ylab=ylab, zlab=zlab, Dlab=Dlab,
                                  spheight=spheight, spwidth=spwidth,
                                  lpheight=lpheight, lpwidth=lpwidth,
                                  rmin=rmin, rmax=rmax, xran=xran, yran=yran,
                                  revz=revz)

        self.zslider = Slider(title=zlab + ' index', start=0, end=z.size-1,
                              step=1, value=0, orientation='horizontal')

        self.zslider.on_change('value', self.splotlp.spplot.inputChange)

        self.children.append(WidgetBox(self.zslider, width=self.width))
        self.children.append(self.splotlp)

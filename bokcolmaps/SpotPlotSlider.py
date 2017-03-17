from .SpotPlot import SpotPlot

from bokeh.models.widgets import Slider
from bokeh.models.layouts import Column, WidgetBox

from bokeh.core.properties import Instance

class SpotPlotSlider(Column):

    '''
    A SpotPlot with a slider linked to the z coordinate (i.e. the row being displayed).
    '''

    sPlot = Instance(SpotPlot)
    zSlider = Instance(Slider)

    __view_model__ = "Column"
    __subtype__ = "SpotPlotSlider"

    def __init__(self,x,y,z,D,palette = 'Viridis256',cfile='jet.txt',
                 xlab='x',ylab='y',zlab='Index',Dlab='Data',
                 height = 575, width = 500,rMin = None,rMax = None,
                 xran = None,yran = None):

        '''
        All init arguments same as for SpotPlot.
        '''

        super().__init__()

        self.height = height
        self.width = int(width*1.1)

        self.sPlot = SpotPlot(x,y,z,D,palette=palette,cfile=cfile,xlab=xlab,ylab=ylab,zlab=zlab,Dlab=Dlab,
                              height=height,width=width,rMin=rMin,rMax=rMax,xran=xran,yran=yran)

        self.zSlider = Slider(title = 'z index',start = 0,end = z.size-1,step = 1,
                              value = 0,orientation='horizontal')

        self.zSlider.on_change('value',self.sPlot.inputChange)

        self.children.append(WidgetBox(self.zSlider,width = self.width))
        self.children.append(self.sPlot)

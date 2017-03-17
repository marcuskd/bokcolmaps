from .SpotPlotLP import SpotPlotLP

from bokeh.models.widgets import Slider
from bokeh.models.layouts import Column, WidgetBox

from bokeh.core.properties import Instance

class SpotPlotLPSlider(Column):

    '''
    A SpotPlotLP with a slider linked to the z coordinate (i.e. the row being displayed).
    '''

    __view_model__ = "Column"
    __subtype__ = "SpotPlotLPSlider"

    sPlotLP = Instance(SpotPlotLP)
    zSlider = Instance(Slider)

    def __init__(self,x,y,z,D,palette = 'Viridis256',cfile='jet.txt',
                 xlab='x',ylab='y',zlab='Index',Dlab='Data',
                 spheight = 575,spwidth = 500,lpheight = 500,lpwidth = 300,
                 rMin = None,rMax = None,xran = None,yran = None,revz = False):

        '''
        All init arguments same as for SpotPlotLP.
        '''

        super(SpotPlotLPSlider,self).__init__()

        self.height = spheight
        self.width = int((spwidth + lpwidth)*1.1)

        self.sPlotLP = SpotPlotLP(x,y,z,D,palette=palette,cfile=cfile,xlab=xlab,ylab=ylab,zlab=zlab,Dlab=Dlab,
                                  spheight=spheight,spwidth=spwidth,lpheight=lpheight,lpwidth=lpwidth,
                                  rMin=rMin,rMax=rMax,xran=xran,yran=yran,revz=revz)

        self.zSlider = Slider(title = zlab + ' index',start = 0,end = z.size-1,step = 1,
                              value = 0,orientation='horizontal')

        self.zSlider.on_change('value',self.sPlotLP.spplot.inputChange)

        self.children.append(WidgetBox(self.zSlider,width = self.width))
        self.children.append(self.sPlotLP)

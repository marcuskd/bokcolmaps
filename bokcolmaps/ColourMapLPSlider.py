from .ColourMapLP import ColourMapLP

from bokeh.models.widgets import Slider
from bokeh.models.layouts import Column, WidgetBox

from bokeh.core.properties import Instance

class ColourMapLPSlider(Column):

    '''
    A ColourMapLP with a slider linked to the z coordinate (i.e. the 2D slice being displayed).
    '''

    __view_model__ = "Column"
    __subtype__ = "ColourMapLPSlider"

    cMapLP = Instance(ColourMapLP)
    zSlider = Instance(Slider)

    def __init__(self,x,y,z,D,palette = 'Viridis256',cfile='jet.txt',
                 xlab='x',ylab='y',zlab='Index',Dlab='Data',
                 cmheight = 575,cmwidth = 500,lpheight = 500,lpwidth = 300,
                 rMin = None,rMax = None,xran = None,yran = None,
                 revz = False,hoverdisp = True):

        '''
        All init arguments same as for ColourMapLP.
        '''

        super().__init__()

        self.height = cmheight
        self.width = int((cmwidth + lpwidth)*1.1)

        self.cMapLP = ColourMapLP(x,y,z,D,palette=palette,cfile=cfile,xlab=xlab,ylab=ylab,zlab=zlab,Dlab=Dlab,
                                  cmheight=cmheight,cmwidth=cmwidth,lpheight=lpheight,lpwidth=lpwidth,
                                  rMin=rMin,rMax=rMax,xran=xran,yran=yran,revz=revz,hoverdisp=hoverdisp)

        self.zSlider = Slider(title = zlab + ' index',start = 0,end = z.size-1,step = 1,
                              value = 0,orientation='horizontal')

        self.zSlider.on_change('value',self.cMapLP.cmplot.inputChange)

        self.children.append(WidgetBox(self.zSlider,width = self.width))
        self.children.append(self.cMapLP)

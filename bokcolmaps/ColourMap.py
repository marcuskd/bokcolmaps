import numpy

from bokeh.plotting import Figure

from bokeh.models import ColumnDataSource, Plot, ColorBar, HoverTool
from bokeh.models.mappers import LinearColorMapper
from bokeh.models.ranges import Range1d
from bokeh.models.tickers import AdaptiveTicker
from bokeh.models.layouts import Column
from bokeh.models.callbacks import CustomJS

from bokeh.core.properties import Instance, String, Float, Bool, Int

class ColourMap(Column):

    '''
    Plots an image as a colour map with a user-defined colour scale and creates a hover readout.
    '''

    __view_model__ = 'Column'
    __subtype__ = 'ColourMap'

    __sizing_mode__ = 'stretch_both'

    plot = Instance(Plot)
    cbar = Instance(ColorBar)

    datasrc = Instance(ColumnDataSource)
    cvals = Instance(ColumnDataSource)

    cmap = Instance(LinearColorMapper)

    titleRoot = String
    zlab = String

    rMin = Float
    rMax = Float
    autoScale = Bool

    xsize = Int
    ysize = Int
    zsize = Int

    cbdelta = Float

    jsCode = String

    def __init__(self,x,y,z,D,palette = 'Viridis256',cfile = 'jet.txt',
                 xlab = 'x',ylab = 'y',zlab = 'Index',Dlab = 'Data',
                 height = 575,width = 500,rMin = None,rMax = None,
                 xran = None,yran = None,hover = True):

        '''
        x,y and z are 1D NumPy arrays for the 3D grid dimensions. D is a 3D NumPy array.
        Supply a bokeh palette name or a file of RGBA floats - this will be used if provided.
        xlab,ylab,zlab,Dlab: labels for the axes and data.
        height and width for the plot are in pixels.
        rMin and rMax are fixed limits for the colour scale (i.e. it won't autoscale).
        xran and yran: ranges for the x and y axes (e.g. to link to another plot).
        hover: enable hover tool readout.
        '''

        super().__init__()

        self.cbdelta = 0.01 # Dummy increment for colourbar range if all values are the same

        self.titleRoot = Dlab
        self.zlab = zlab

        self.rMin = rMin
        self.rMax = rMax
        self.autoScale = True
        if (self.rMin is not None) and (self.rMax is not None): self.autoScale = False

        if len(D.shape) == 2: self.ysize,self.xsize = D.shape
        elif len(D.shape) == 3: self.zsize,self.ysize,self.xsize = D.shape

        if len(D.shape) > 2: # Default to zero depth
            d = D[0]
        else:
            d = D

        D = D.flatten()

        # All variables stored as single item lists in order to be the same length (as required by ColumnDataSource)
        self.datasrc = ColumnDataSource(data={'x':[x],'y':[y],'z':[z],'image':[d],'D':[D],
                                              'xp':[0],'yp':[0],'dp':[0]})

        if self.autoScale:
            dfi = d[numpy.isfinite(d)]
            if (dfi.size > 0):
                minVal = dfi.min()
                maxVal = dfi.max()
                if maxVal == minVal:
                    maxVal += self.cbdelta
            else:
                minVal = 0
                maxVal = self.cbdelta
        else:
            minVal = self.rMin
            maxVal = self.rMax

        if cfile is not None:
            self.readCMap(cfile)
            self.cmap = LinearColorMapper(palette = self.cvals.data['colours'])
        else:
            self.cmap = LinearColorMapper(palette = palette)
        self.cmap.low = minVal
        self.cmap.high = maxVal

        if xran == None: # Default to entire range unless externally controlled
            xran = Range1d(start = x[0],end = x[-1])
        if yran == None:
            yran = Range1d(start = y[0],end = y[-1])

        ptools = ['reset,pan,resize,wheel_zoom,box_zoom,save']

        # JS code defined whether or not hover tool used as may be needed in derived class ColourMapLP
        self.jsCode = '''
        var geom = cb_data['geometry'];
        var data = datasrc.get('data');

        var hx = geom.x;
        var hy = geom.y;

        var x = data['x'][0];
        var y = data['y'][0];
        var d = data['image'][0];

        var dx = x[1] - x[0];
        var dy = y[1] - y[0];
        var xind = Math.floor((hx + dx/2 - x[0])/dx);
        var yind = Math.floor((hy + dy/2 - y[0])/dy);

        if ((xind < x.length) && (yind < y.length)) {
            data['xp'] = [x[xind]];
            data['yp'] = [y[yind]];
            var zind = yind*x.length + xind;
            data['dp'] = [d[zind]];
        }
        '''

        if hover:
            cJS = CustomJS(args = {'datasrc':self.datasrc},code = self.jsCode)
            htool = HoverTool(tooltips=[(xlab,'@xp{0.00}'),(ylab,'@yp{0.00}'),(Dlab,'@dp{0.00}')],
                              callback = cJS,point_policy = 'follow_mouse')
            ptools.append(htool)

        self.plot = Figure(x_axis_label = xlab,y_axis_label = ylab,
                           x_range = xran,y_range = yran,
                           plot_height = height,plot_width = width,
                           tools=ptools,toolbar_location='right')

        self.updateTitle(0)

        self.plot.title.text_font = 'garamond'
        self.plot.title.text_font_size = '12pt'
        self.plot.title.text_font_style = 'bold'
        self.plot.title.align = 'center'

        dx = abs(x[1] - x[0])
        dy = abs(y[1] - y[0])

        pw = abs(x[-1]-x[0])+dx
        ph = abs(y[-1]-y[0])+dy

        # The image is displayed such that x and y coordinate values correspond to the centres of rectangles

        xs = xran.start
        if xran.end > xran.start: xs -= dx/2
        else: xs += dx/2
        ys = yran.start
        if yran.end > yran.start: ys -= dy/2
        else: ys += dy/2

        self.plot.image('image',source = self.datasrc,x = xs,y = ys,
                        dw = pw,dh = ph,color_mapper = self.cmap)

        self.plot.rect(x = (x[0]+x[-1])/2,y = (y[0]+y[-1])/2,width = pw, height = ph,
                       line_alpha = 0,fill_alpha = 0,source = self.datasrc) # Needed for HoverTool

        self.plot.xaxis.axis_label_text_font = 'garamond'
        self.plot.xaxis.axis_label_text_font_size = '10pt'
        self.plot.xaxis.axis_label_text_font_style = 'bold'

        self.plot.yaxis.axis_label_text_font = 'garamond'
        self.plot.yaxis.axis_label_text_font_size = '10pt'
        self.plot.yaxis.axis_label_text_font_style = 'bold'

        self.generateColorbar(cbarwidth = round(width/20))

        self.children.append(self.plot)

    def generateColorbar(self,cbarwidth = 25):

        self.cbar = ColorBar(color_mapper = self.cmap, location=(0,0), label_standoff = 5,
                             orientation='horizontal', height = cbarwidth,
                             ticker = AdaptiveTicker(), border_line_color = None,
                             bar_line_color = 'black',major_tick_line_color = 'black',
                             minor_tick_line_color = None)

        self.plot.add_layout(self.cbar,'below')

    def readCMap(self,fname):

        '''
        Read in the colour scale.
        '''

        f = open(fname,'rt')
        cmap = []
        for l in f:
            valstrs = l[:-1].split(',')
            vals = []
            for s in valstrs[:-1]:
                vals.append(round(255*float(s)))
            vtup = tuple(vals)
            cmap.append('#%02x%02x%02x' % vtup) # Format as hex triple
        f.close()
        self.cvals = ColumnDataSource(data = {'colours':cmap})

    def changed(self,zind):

        '''
        Change the 2D slice of D being displayed (i.e. a different value of z)
        '''

        if (zind >= 0) and (zind < self.zsize):
            zindl = zind*self.xsize*self.ysize
            data = self.datasrc.data
            d = self.datasrc.data['image'][0]
            D = data['D'][0]
            d = D[zindl:zindl + self.xsize*self.ysize]
            d = d.reshape((self.ysize,self.xsize))
            data['image'] = [d]

    def updateCbar(self):

        '''
        Update the colour scale (needed when the data for display changes).
        '''

        if self.autoScale:
            d = self.datasrc.data['image'][0]
            dfi = d[numpy.isfinite(d)]
            if (dfi.size > 0):
                minVal = dfi.min()
                maxVal = dfi.max()
                if maxVal == minVal:
                    maxVal += self.cbdelta
            else:
                minVal = 0
                maxVal = self.cbdelta
            self.cmap.low = minVal
            self.cmap.high = maxVal

    def updateTitle(self,zind):

        if len(self.datasrc.data['z'][0]) > 1:
            self.plot.title.text = self.titleRoot + ', ' + self.zlab + ' = ' + str(self.datasrc.data['z'][0][zind])
        else:
            self.plot.title.text = self.titleRoot

    def inputChange(self,attrname,old,new):

        '''
        Callback for use with e.g. sliders.
        '''

        self.changed(new)
        self.updateCbar()
        self.updateTitle(new)

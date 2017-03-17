import numpy

from bokeh.plotting import Figure

from bokeh.models import ColumnDataSource, Plot, ColorBar
from bokeh.models.mappers import LinearColorMapper
from bokeh.models.tickers import AdaptiveTicker
from bokeh.models.layouts import Column

from bokeh.core.properties import Instance, String, Int, Float, Bool

class SpotPlot(Column):

    '''
    Like a scatter plot but with the points colour mapped with a user-defined colour scale.
    '''

    __view_model__ = "Column"
    __subtype__ = "SpotPlot"

    __sizing_mode__ = 'stretch_both'

    plot = Instance(Plot)
    cbar = Instance(ColorBar)

    datasrc = Instance(ColumnDataSource)
    coldatasrc = Instance(ColumnDataSource)
    cvals = Instance(ColumnDataSource)
    cmap = Instance(LinearColorMapper)

    titleRoot = String
    zlab = String
    bgCol = String
    nanCol = String
    spSize = Int
    rMin = Float
    rMax = Float
    autoScale = Bool
    cbdelta = Float

    def __init__(self,x,y,z,D,palette = 'Viridis256',cfile = 'jet.txt',
                 xlab = 'x',ylab = 'y',zlab = 'Index',Dlab = 'Data',
                 height = 575,width = 500,rMin = None,rMax = None,
                 xran = None,yran = None,ttool = None):

        '''
        x and y (same length) give the spot locations, z is the (common) z axis. All are 1D NumPy arrays.
        D is a 2D NumPy array of the data for display, dimensions z.size by x.size (or y.size).
        Supply a bokeh palette name or a file of RGBA floats - this will be used if provided.
        xlab,ylab,zlab,Dlab: labels for the axes and data.
        height and width for the plot are in pixels.
        rMin and rMax are fixed limits for the colour scale (i.e. it won't autoscale).
        xran and yran: ranges for the x and y axes (e.g. to link to another plot).
        ttool: custom tap tool passed in from SpotPlotLP class.
        '''

        super().__init__()

        self.cbdelta = 0.01 # Dummy increment for colourbar range if all values are the same

        self.titleRoot = Dlab
        self.zlab = zlab

        self.rMin = rMin
        self.rMax = rMax
        self.autoScale = True
        if (self.rMin is not None) & (self.rMax is not None): self.autoScale = False

        if z.size > 1: # Default to zero depth
            d = D[0]
        else:
            d = D

        dfi = d[numpy.isfinite(d)]
        if self.autoScale:
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
            self.cvals = ColumnDataSource(data = {'colours':self.cmap.palette})
        self.cmap.low = minVal
        self.cmap.high = maxVal

        self.bgCol = 'black'
        self.nanCol = 'grey'
        self.spSize = int(min(height,width)/25)

        cols = [self.nanCol]*d.size # Initially empty
        self.datasrc = ColumnDataSource(data={'z':[z],'d':[d],'D':[D]})
        self.coldatasrc = ColumnDataSource(data={'x':x,'y':y,'cols':cols})

        ptools = ["reset,pan,resize,wheel_zoom,box_zoom,save"]
        if ttool is not None: ptools.append(ttool)

        if xran is None: xran = [x.min(),x.max()] # Default to entire range unless externally controlled
        if yran is None: yran = [y.min(),y.max()]

        self.plot = Figure(x_axis_label = xlab,y_axis_label = ylab,
                           x_range = xran,y_range = yran,
                           plot_height = height,plot_width = width,
                           background_fill_color = self.bgCol,
                           tools = ptools,toolbar_location='right')

        self.plot.circle('x','y',size = self.spSize,color = 'cols',source = self.coldatasrc,
                         nonselection_fill_color = 'cols', selection_fill_color = 'cols',
                         nonselection_fill_alpha = 1, selection_fill_alpha = 1,
                         nonselection_line_alpha = 0, selection_line_alpha = 1,
                         nonselection_line_color = 'cols', selection_line_color = 'white',
                         line_width = 5)

        self.updateTitle(0)

        self.plot.title.text_font = 'garamond'
        self.plot.title.text_font_size = '12pt'
        self.plot.title.text_font_style = 'bold'
        self.plot.title.align = 'center'

        self.plot.xaxis.axis_label_text_font = 'garamond'
        self.plot.xaxis.axis_label_text_font_size = '10pt'
        self.plot.xaxis.axis_label_text_font_style = 'bold'

        self.plot.yaxis.axis_label_text_font = 'garamond'
        self.plot.yaxis.axis_label_text_font_size = '10pt'
        self.plot.yaxis.axis_label_text_font_style = 'bold'

        self.updateColours()

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
        Change the row of D being displayed (i.e. a different value of z)
        '''

        if (zind >= 0) & (zind < self.datasrc.data['D'][0].shape[0]):
            data = self.datasrc.data
            newdata = data
            d = data['D'][0][zind]
            newdata['d'] = [d]
            self.datasrc.trigger('data',data,newdata)

    def updateCbar(self):

        '''
        Update the colour scale (needed when the data for display changes).
        '''

        if self.autoScale:
            d = self.datasrc.data['d'][0]
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

        if self.datasrc.data['z'][0].size > 1: val = self.datasrc.data['z'][0][zind]
        else: val = self.datasrc.data['z'][0]
        self.plot.title.text = self.titleRoot + ', ' + self.zlab + ' = ' + str(val)

    def inputChange(self,attrname,old,new):

        '''
        Callback for use with e.g. sliders.
        '''

        self.convertData()
        self.changed(new)
        self.updateCbar()
        self.updateColours()
        self.updateTitle(new)

    def updateColours(self):

        '''
        Update the spot colours (needed when the data for display changes).
        '''

        colset = self.cvals.data['colours']
        ncols = len(colset)

        d = self.datasrc.data['d'][0]

        data = self.coldatasrc.data
        newdata = data
        cols = data['cols']

        minVal = self.cmap.low
        maxVal = self.cmap.high

        for s in range(d.size):
            if numpy.isfinite(d[s]):
                cind = int(round(ncols*(d[s] - minVal)/(maxVal - minVal)))
                if cind < 0: cind = 0
                if cind >= ncols: cind = ncols - 1
                cols[s] = colset[cind]
            else:
                cols[s] = self.nanCol

        newdata['cols'] = cols
        self.coldatasrc.trigger('data',data,newdata)

    def convertData(self):

        '''
        NumPy arrays sometimes not deserialised from lists so need to check.
        '''

        data = self.datasrc.data
        newdata = data
        for k in ['z','d','D']:
            if type(newdata[k][0]) is list:
                newdata[k][0] = numpy.array(newdata[k][0])

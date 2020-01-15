"""
ColourMap3 class definition
"""

from bokeh.plotting import Figure

from bokeh.models import ColumnDataSource, Plot, ColorBar, HoverTool
from bokeh.models.mappers import LinearColorMapper
from bokeh.models.ranges import Range1d
from bokeh.models.layouts import Column
from bokeh.models.callbacks import CustomJS

from bokeh.core.properties import Instance, String, Float, Bool, Int

from bokcolmaps.get_common_kwargs import get_common_kwargs
from bokcolmaps.generate_colourbar import generate_colourbar
from bokcolmaps.read_colourmap import read_colourmap
from bokcolmaps.get_min_max import get_min_max


class ColourMap3(Column):

    """
    This provides the same functionality as the ColourMap class
    without requiring the Bokeh Server (i.e. works with static HTML).
    """

    __view_model__ = 'Column'
    __subtype__ = 'ColourMap3'

    __view_module__ = 'bokeh'

    __sizing_mode__ = 'stretch_both'

    plot = Instance(Plot)
    cbar = Instance(ColorBar)

    datasrc = Instance(ColumnDataSource)
    mmsrc = Instance(ColumnDataSource)
    cvals = Instance(ColumnDataSource)

    cmap = Instance(LinearColorMapper)

    title_root = String
    zlab = String

    rmin = Float
    rmax = Float
    autoscale = Bool

    xsize = Int
    ysize = Int
    zsize = Int

    cbdelta = Float

    js_hover = String

    cjs_slider = Instance(CustomJS)

    def __init__(self, x, y, z, dm, **kwargs):

        """
        args...
            x: 1D NumPy array of x coordinates
            y: 1D NumPy array of y coordinates
            z: 1D NumPy array of y coordinates
            dm: 3D NumPy array of the data for display, dimensions z.size, y.size, x.size
        kwargs: all in get_common_kwargs plus...
            height: plot height (pixels)
            width: plot width (pixels)
            hover: Boolean to enable hover tool readout
        """

        palette, cfile, xlab, ylab, zlab,\
            dmlab, rmin, rmax, xran, yran = get_common_kwargs(**kwargs)

        height = kwargs.get('height', 575)
        width = kwargs.get('width', 500)
        hover = kwargs.get('hover', True)

        super().__init__()

        self.cbdelta = 0.01  # Min colourbar range (used if values are equal)

        self.title_root = dmlab
        self.zlab = zlab

        self.rmin = rmin
        self.rmax = rmax
        self.autoscale = True
        if (self.rmin is not None) and (self.rmax is not None):
            self.autoscale = False

        if len(dm.shape) == 2:
            self.ysize, self.xsize = dm.shape
            self.zsize = 1
        elif len(dm.shape) == 3:
            self.zsize, self.ysize, self.xsize = dm.shape

        if len(dm.shape) > 2:  # Default to first slice
            d = dm[0]
        else:
            d = dm

        # Get minimum and maximum values for the colour mapping

        minvals = [None] * self.zsize
        maxvals = [None] * self.zsize
        for zind in range(self.zsize):
            minvals[zind], maxvals[zind] = get_min_max(dm[zind], self.cbdelta)
        self.mmsrc = ColumnDataSource(data={'minvals': minvals, 'maxvals': maxvals})

        dm = dm.flatten()

        # All variables stored as single item lists in order to be the same
        # length (as required by ColumnDataSource)
        self.datasrc = ColumnDataSource(data={'x': [x], 'y': [y], 'z': [z],
                                              'image': [d], 'dm': [dm],
                                              'xp': [0], 'yp': [0], 'dp': [0]})

        # JS code for slider in classes ColourMap3Slider
        # and ColourMap3LPSlider

        js_slider = """
        var dind = cb_obj['value'];
        var data = datasrc.data;

        var x = data['x'][0];
        var y = data['y'][0];
        var d = data['image'][0];
        var dm = data['dm'][0];

        var nx = x.length;
        var ny = y.length;

        var sind = dind*nx*ny;
        for (i=0; i<nx*ny; i++) {
            d[i] = dm[sind+i];
        }

        datasrc.change.emit();

        var minval = mmsrc.data['minvals'][dind];
        var maxval = mmsrc.data['maxvals'][dind];

        cmap.low = minval;
        cmap.high = maxval;

        var z = data['z'][0];
        cmplot.title.text = title_root + ', ' + zlab + ' = ' + z[dind].toString();
        """

        self.get_cmap(cfile, palette)

        if xran is None:  # Default to whole range unless externally controlled
            xran = Range1d(start=x[0], end=x[-1])
        if yran is None:
            yran = Range1d(start=y[0], end=y[-1])

        ptools = ['reset, pan, wheel_zoom, box_zoom, save']

        # JS code defined whether or not hover tool used as may be needed in
        # class ColourMapLP

        self.js_hover = """
        var geom = cb_data['geometry'];
        var data = datasrc.data;

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
        """

        if hover:
            cjs_hover = CustomJS(args={'datasrc': self.datasrc},
                                 code=self.js_hover)
            htool = HoverTool(tooltips=[(xlab, '@xp{0.00}'),
                                        (ylab, '@yp{0.00}'),
                                        (dmlab, '@dp{0.00}')],
                              callback=cjs_hover, point_policy='follow_mouse')
            ptools.append(htool)

        # Create the plot

        self.plot = Figure(x_axis_label=xlab, y_axis_label=ylab,
                           x_range=xran, y_range=yran,
                           plot_height=height, plot_width=width,
                           tools=ptools, toolbar_location='right')

        self.cjs_slider = CustomJS(args={'datasrc': self.datasrc, 'mmsrc': self.mmsrc,
                                         'cmap': self.cmap, 'cmplot': self.plot,
                                         'title_root': self.title_root, 'zlab': self.zlab},
                                   code=js_slider)

#       Set the title

        if len(self.datasrc.data['z'][0]) > 1:
            self.plot.title.text = self.title_root + ', ' + \
                self.zlab + ' = ' + str(self.datasrc.data['z'][0][zind])
        else:
            self.plot.title.text = self.title_root

        self.plot.title.text_font = 'garamond'
        self.plot.title.text_font_size = '12pt'
        self.plot.title.text_font_style = 'bold'
        self.plot.title.align = 'center'

        # The image is displayed such that x and y coordinate values
        # correspond to the centres of rectangles

        dx = abs(x[1] - x[0])
        dy = abs(y[1] - y[0])

        pw = abs(x[-1] - x[0]) + dx
        ph = abs(y[-1] - y[0]) + dy

        xs = xran.start
        if xs is None:
            xs = 0
        elif xran.end > xran.start:
            xs -= dx / 2
        else:
            xs += dx / 2
        ys = yran.start
        if ys is None:
            ys = 0
        elif yran.end > yran.start:
            ys -= dy / 2
        else:
            ys += dy / 2

        self.plot.image('image', source=self.datasrc, x=xs, y=ys,
                        dw=pw, dh=ph, color_mapper=self.cmap)

        # Needed for HoverTool...

        self.plot.rect(x=(x[0] + x[-1]) / 2, y=(y[0] + y[-1]) / 2, width=pw, height=ph,
                       line_alpha=0, fill_alpha=0, source=self.datasrc)

        self.plot.xaxis.axis_label_text_font = 'garamond'
        self.plot.xaxis.axis_label_text_font_size = '10pt'
        self.plot.xaxis.axis_label_text_font_style = 'bold'

        self.plot.yaxis.axis_label_text_font = 'garamond'
        self.plot.yaxis.axis_label_text_font_size = '10pt'
        self.plot.yaxis.axis_label_text_font_style = 'bold'

        self.cbar = generate_colourbar(self.cmap, cbarwidth=round(height / 20))
        self.plot.add_layout(self.cbar, 'below')

        self.children.append(self.plot)

    def get_cmap(self, cfile, palette):

        """
        Get the colour mapper
        """

        if self.autoscale:
            min_val, max_val = get_min_max(self.datasrc.data['image'][0],
                                           self.cbdelta)
        else:
            min_val = self.rmin
            max_val = self.rmax

        if cfile is not None:
            self.read_cmap(cfile)
            self.cmap = LinearColorMapper(palette=self.cvals.data['colours'])
        else:
            self.cmap = LinearColorMapper(palette=palette)
        self.cmap.low = min_val
        self.cmap.high = max_val

    def read_cmap(self, fname):

        """
        Read in the colour scale.
        """

        self.cvals = read_colourmap(fname)

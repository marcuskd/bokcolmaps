"""
To run this example at the command line enter:
python3 ColourMap3LPSLiderExample.py
"""

from bokeh.plotting import show

from bokcolmaps.ColourMap3LPSlider import ColourMap3LPSlider
from bokcolmaps.Examples import example_data

x, y, z, D = example_data()

cm = ColourMap3LPSlider(x, y, z, D, cfile='../jet.txt',
                        xlab='x val', ylab='y val', zlab='power val',
                        dmlab='Function val')

show(cm)

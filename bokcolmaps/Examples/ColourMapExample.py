# To run this example at the command line enter: python3 ColourMapExample.py

import numpy

from bokeh.plotting import show

from bokcolmaps import ColourMap
from bokcolmaps.Examples.ExampleData import ExampleData

x,y,z,D = ExampleData()
D = D[0] # Data for first value of z
z = numpy.array([z[0]]) # First value of z

cm = ColourMap(x,y,z,D,cfile='../jet.txt',
               xlab='x val',ylab='y val',zlab='power val',Dlab='Function val')

show(cm)

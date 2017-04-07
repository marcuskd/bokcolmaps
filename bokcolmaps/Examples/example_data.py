# Arbitrary data used for the examples, generated by simple function f = (xy)**z

import numpy

def example_data():

    x = numpy.linspace(1,2,11) # x and y must be uniformly spaced for ColourMap class
    y = numpy.linspace(2,4,21)
    z = numpy.array([0.5,0.8,1,1.5,2.5,3.1]) # z can be non-uniformly spaced
    nx, ny, nz = x.size, y.size, z.size

    D = numpy.ndarray([nz, ny, nx])

    for i in range(nz):
        for j in range(ny):
            for k in range(nx):
                D[i, j, k] = (y[j]*x[k])**z[i]

    return x, y, z, D
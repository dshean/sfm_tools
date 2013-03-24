#! /usr/bin/env python

#David Shean
#dshean@gmail.com
#3/1/13

#Script to compute resolution and fov for Nikon D800 for variable focal length and range

import sys
import numpy
import matplotlib.pyplot as plt

x_mm = 35.9
y_mm = 24
x_px = 7360
y_px = 4912

diag_mm = numpy.sqrt(x_mm**2 + y_mm**2)
diag_px = numpy.sqrt(x_px**2 + y_px**2)

def calcfov(f):
    return 2*numpy.arctan2(diag_mm, (2*f))

def calcres(alt, fov):
    #Convert feet to m
    res = 2*alt*numpy.tan(fov/2)/diag_px
    return res/numpy.cos(numpy.radians(offnadir))

def plotgen(alt_list, f_list):
    alt_range = numpy.arange(alt_list[0], alt_list[-1], 100) 
    for f in f_list:
        fov = calcfov(f)
        res = calcres(alt_range, fov)
        x_gd = numpy.array(res)*x_px 
        plt.figure(1)
        plt.plot(alt_range/0.3048, res*100, label='%i mm' % f)
        plt.figure(2)
        plt.plot(alt_range/0.3048, x_gd, label='%i mm' % f)
    
    plt.figure(1)
    plt.xlabel('Distance (ft)')
    plt.ylabel('Resolution (cm)')
    plt.legend(loc=2)
    
    plt.figure(2)
    plt.xlabel('Distance (ft)')
    plt.ylabel('X field of view (m)')
    plt.legend(loc=2)
    
    plt.show()

offnadir = 0 
alt_list = numpy.array([500, 1500, 3000, 6000, 12000, 24000])
alt_list *= 0.3048
f_list = numpy.array([16.0, 28.0, 50.0, 85.0, 300.0])

plotgen(alt_list, f_list)

sys.exit()

print offnadir, "degrees off-nadir"
for alt in alt_list:
    for f in f_list:
        fov = calcfov(f)
        res = calcres(alt, fov)
        x_gd = res*x_px
        print "alt: %s', fl: %0i mm, fov: %0.1f deg, res: %0.1f cm, x_dist: %0.1f m" % (alt, f, numpy.degrees(fov), res*100, x_gd)
        #print alt_m, x_gd 
        #print "alt: %s' fl: %0i mm res: %0.1f cm" % (alt, f, res*100)
    print

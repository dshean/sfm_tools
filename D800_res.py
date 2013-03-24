#! /usr/bin/env python

#David Shean
#dshean@gmail.com
#3/1/13

#Script to compute resolution and fov for Nikon D800 for variable focal length and range

import math

x_mm = 35.9
y_mm = 24
x_px = 7360
y_px = 4912

diag_mm = math.sqrt(x_mm**2 + y_mm**2)
diag_px = math.sqrt(x_px**2 + y_px**2)

def calcfov(f):
    return 2*math.atan2(diag_mm, (2*f))

def calcres(alt, fov):
    return 2*alt*math.tan(fov/2)/diag_px

offnadir = 45 
#offnadir = 0 
alt_list = [500, 1500, 3000, 6000, 12000]
f_list = [16.0, 28.0, 50.0, 85.0, 300.0]

print offnadir, "degrees off-nadir"
for alt in alt_list:
    alt_m = alt * 0.3048
    for f in f_list:
        fov = calcfov(f)
        res = calcres(alt_m, fov)
        res *= 1/math.cos(math.radians(offnadir))
        x_gd = res*x_px
        print "alt: %s', fl: %0i mm, fov: %0.1f deg, res: %0.1f cm, x_dist: %0.1f m" % (alt, f, math.degrees(fov), res*100, x_gd)
        #print alt_m, x_gd 
        #print "alt: %s' fl: %0i mm res: %0.1f cm" % (alt, f, res*100)
    print

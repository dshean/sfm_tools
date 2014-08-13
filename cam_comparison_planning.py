#! /usr/bin/env python

#David Shean
#dshean@gmail.com
#3/1/13

#Script to compute resolution and fov for Nikon D800 for variable focal length and range

import sys
import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle

def calcfov(cam, f):
    fov = 2*np.arctan2(cam['diag_mm'], (2*f))
    #print np.degrees(fov)
    return fov

def calcres(cam, alt, fov, offnadir=0):
    res = 2*alt*np.tan(fov/2)/cam['diag_px']
    #return res/np.cos(np.radians(offnadir))
    return res/np.cos(offnadir)

def plotgen(cam, alt_range):
    c = next(colorcycler)
    linecycler = cycle(lines)
    if alt_units == 'ft':
        alt_scale = 0.3048
    else:
        alt_scale = 1.0
    for f in cam['f_list']:
        fov = calcfov(cam, f)
        res_center = calcres(cam, alt_range, fov, offnadir=0)
        res_corner = calcres(cam, alt_range, fov, offnadir=fov/2.)
        x_gd = np.array(res_center)*cam['x_px'] 
        y_gd = np.array(res_center)*cam['y_px'] 
        gd_area = x_gd * y_gd
        #ls = next(linecycler)
        ls = '-'
        plt.figure(1)
        plt.plot(alt_range/alt_scale, res_center*100, color=c, ls=ls, label='%s, %0.1f mm (%0.1f$^\circ$, %0.1f mm eq) Center' % (cam['name'],f,np.degrees(fov),f*cam['crop_factor']))
        plt.plot(alt_range/alt_scale, res_corner*100, color=c, ls='--', label='%s, %0.1f mm (%0.1f$^\circ$, %0.1f mm eq) Corner' % (cam['name'],f,np.degrees(fov),f*cam['crop_factor']))
        plt.figure(2)
        plt.plot(alt_range/alt_scale, x_gd, color=c, ls=ls, label='%s, %0.1f mm (%0.1f$^\circ$, %0.1f mm eq)' % (cam['name'],f,np.degrees(fov),f*cam['crop_factor']))
        plt.figure(3)
        plt.plot(alt_range/alt_scale, y_gd, color=c, ls=ls, label='%s, %0.1f mm (%0.1f$^\circ$, %0.1f mm eq)' % (cam['name'],f,np.degrees(fov),f*cam['crop_factor']))
        plt.figure(4)
        plt.plot(alt_range/alt_scale, gd_area, color=c, ls=ls, label='%s, %0.1f mm (%0.1f$^\circ$, %0.1f mm eq)' % (cam['name'],f,np.degrees(fov),f*cam['crop_factor']))
    
offnadir = 0 
#Altitude range in feet
#alt_units = 'ft'
#alt_list = np.arange(0, 401, 10)
#if alt_units == 'ft':
#    alt_list *= 0.3048
#Altitude range in meters
alt_units = 'm'
alt_list = np.arange(0, 122, 4)

d800 = {'name':'D800', 'x_mm':35.9, 'y_mm':24.0, 'x_px':7360, 'y_px':4912, 'f_list': (50.0,) }
#NEX5 = {'name':'NEX-5', 'x_mm':23.4, 'y_mm':15.6, 'x_px':4912, 'y_px':3264, 'f_list': (16.0, 20.0) }
NEX5 = {'name':'NEX-5', 'x_mm':23.4, 'y_mm':15.6, 'x_px':4912, 'y_px':3264, 'f_list': (20.0,) }
a5000 = {'name':'a5000', 'x_mm':23.4, 'y_mm':15.6, 'x_px':5456, 'y_px':3632, 'f_list': (16.0, 20.0) }
#rx100 = {'name':'rx100_III', 'x_mm':13.2, 'y_mm':8.8, 'x_px':5472, 'y_px':3648, 'f_list': (8.8, 25.7) }
rx100 = {'name':'RX100_III', 'x_mm':13.2, 'y_mm':8.8, 'x_px':5472, 'y_px':3648, 'f_list': (8.8,) }
gx1 = {'name':'GX1', 'x_mm':17.3, 'y_mm':13.0, 'x_px':4592, 'y_px':3448, 'f_list': (14.0, 20.0) }
s100 = {'name':'s100', 'x_mm':7.6, 'y_mm':5.7, 'x_px':4000, 'y_px':3000, 'f_list': (5.2,) }
gopro12 = {'name':'gopro_12MP', 'x_mm':6.17, 'y_mm':4.55, 'x_px':4000, 'y_px':3000, 'f_list': (2.77,) }
gopro7 = {'name':'gopro_7MP', 'x_mm':4.6275, 'y_mm':3.4125, 'x_px':3000, 'y_px':2250, 'f_list': (2.77,) }

#cams = [d800, NEX5, a5000, gx1, rx100, s100, gopro12, gopro7]
cams = [d800, NEX5, s100, gopro12, gopro7]
cams = cams[::-1]

lines = ["-","--","-.",":"]
colors = ['r','b','g','y','c','m','k','0.5']
colors = colors[::-1]
colorcycler = cycle(colors)
diag_px_35mm = 43.3 

for cam in cams: 
    cam['diag_mm'] = np.sqrt(cam['x_mm']**2 + cam['y_mm']**2)
    cam['diag_px'] = np.sqrt(cam['x_px']**2 + cam['y_px']**2)
    cam['pitch'] = cam['x_mm']/cam['x_px']
    cam['crop_factor'] = diag_px_35mm/cam['diag_mm'] 
    plotgen(cam, alt_list)

plt.figure(1)
plt.grid(b=True, which='major', color='k', linestyle=':', linewidth=0.2)
#plt.grid(b=True, which='minor', color='k', linestyle=':', linewidth=0.2)
plt.gca().minorticks_on()
plt.title('Camera Altitude vs. Ground Sample Distance (best possible pixel res)')
plt.xlabel('Altitude (%s)' % alt_units)
plt.ylabel('GSD (cm)')
plt.legend(loc=2,prop={'size':8})

plt.figure(2)
plt.grid(b=True, which='major', color='k', linestyle=':', linewidth=0.2)
#plt.grid(b=True, which='minor', color='k', linestyle=':', linewidth=0.2)
plt.gca().minorticks_on()
plt.title('Camera Altitude vs. Image Width (on ground)')
plt.xlabel('Altitude (%s)' % alt_units)
plt.ylabel('X field of view (m)')
plt.legend(loc=2,prop={'size':8})

plt.figure(3)
plt.grid(b=True, which='major', color='k', linestyle=':', linewidth=0.2)
#plt.grid(b=True, which='minor', color='k', linestyle=':', linewidth=0.2)
plt.gca().minorticks_on()
plt.title('Camera Altitude vs. Image Height (on ground)')
plt.xlabel('Altitude (%s)' % alt_units)
plt.ylabel('Y field of view (m)')
plt.legend(loc=2,prop={'size':8})

plt.figure(4)
plt.grid(b=True, which='major', color='k', linestyle=':', linewidth=0.2)
#plt.grid(b=True, which='minor', color='k', linestyle=':', linewidth=0.2)
plt.gca().minorticks_on()
plt.title('Camera Altitude vs. Image Area (on ground)')
plt.xlabel('Altitude (%s)' % alt_units)
plt.ylabel('Image area (m^2)')
plt.legend(loc=2,prop={'size':8})

plt.figure(5)
plt.title('Camera Pixel Pitch (sensor pixel size)')
plt.scatter(range(0,len(cams)), [(cam['pitch']*1000.0)**2 for cam in cams], color=colors) 
plt.xticks(range(0,len(cams)), [cam['name'] for cam in cams])
plt.ylabel('Pixel Pitch (micron^2)')
plt.gca().tick_params(axis='x', labelsize=8)
plt.savefig('pixel_pitch.pdf')

plt.figure(1)
plt.savefig('alt_vs_gsd.pdf')
plt.figure(2)
plt.savefig('alt_vs_xfov.pdf')
plt.figure(3)
plt.savefig('alt_vs_yfov.pdf')
plt.figure(4)
plt.savefig('alt_vs_area.pdf')

#plt.show()
sys.exit()

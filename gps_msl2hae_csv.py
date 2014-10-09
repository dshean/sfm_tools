#! /usr/bin/env python 

#David Shean
#dshean@gmail.com
#8/13/14

#This tool reads a csv dump from exiftool and replaces the default MSL GPSAltitude with HAE using PROJ4 
#Requires functions present in demtools/geolib

#Proj4 requires the following to be present
#cd /usr/local/share/proj
#wget http://download.osgeo.org/proj/vdatum/egm96_15/egm96_15.gtx
#wget http://download.osgeo.org/proj/vdatum/egm08_25/egm08_25.gtx

import sys
import os
import numpy as np

import geolib
import genlib

#Load csv
fn = sys.argv[1]
outfn = os.path.splitext(fn)[0]+'_hae.csv' 

#Import csv file to numpy recarray
#The comments hack is for handling files with # in the field names
#ra = np.genfromtxt(fn, delimiter=',', comments='ASDFASDF', names=True, dtype=None, filling_values=' ')
#lat, lon, z = ra['$GPSLatitude#'], ra['$GPSLongitude#'], ra['$GPSAltitude#']
#Had to hardcode these dtype lengths to prevent clipping with dtype=None
dtype=[('SourceFile', 'S255'), ('GPSLatitude', '<f8'), ('GPSLongitude', '<f8'), ('GPSAltitude', '<f8'), ('GPSMapDatum', 'S64')]
ra = np.genfromtxt(fn, delimiter=',', names=True, dtype=dtype)
lat, lon, z = ra['GPSLatitude'], ra['GPSLongitude'], ra['GPSAltitude']

#Convert altitude
newlon, newlat, newz = geolib.geoid2ell(lon, lat, z)

#Sanity check
print 'First input altitude change:'
print ra['GPSAltitude'][0]
print newz[0]

#Replace altitude values
ra['GPSAltitude'] = newz
#Replace datum tag - so we know what we've already updated
new_datum = str('WGS 84 HAE')
ra['GPSMapDatum'] = new_datum 

#This is the only real option to save the recarray to csv
genlib.write_recarray(outfn, ra)

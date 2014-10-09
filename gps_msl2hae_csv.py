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

#Load into object array - should preserve everything as str
ra = np.genfromtxt(fn, delimiter=',', names=True, dtype='O')

#Determine type of input file
if 'SourceFile' in ra.dtype.names:
    intype = 'exif'
elif 'GPS_TimeMS' in ra.dtype.names:
    intype = 'px4_gps'
#Note: CAM altitude is relative!
elif 'CAM_GPSTime' in ra.dtype.names:
    intype = 'px4_cam'
elif 'DateTime' in ra.dtype.names:
    intype = 'px4_utc'
elif 'altitude_feet' in ra.dtype.names:
    intype = 'flytrex'
else:
    sys.exit('Input format not recognized')

#Default altitude factor, assuming meters
alt_factor = 1.0

if intype is 'exif':
    #dtype=[('SourceFile', 'S255'), ('GPSLatitude', '<f8'), ('GPSLongitude', '<f8'), ('GPSAltitude', '<f8'), ('GPSMapDatum', 'S64')]
    #ra = np.genfromtxt(fn, delimiter=',', names=True, dtype=dtype)
    latf = 'GPSLatitude'
    lonf = 'GPSLongitude'
    altf = 'GPSAltitude'
elif intype is 'px4_gps':
    latf = 'GPS_Lat'
    lonf = 'GPS_Lng'
    altf = 'GPS_Alt'
elif intype is 'px4_cam':
    latf = 'CAM_Lat'
    lonf = 'CAM_Lng'
    altf = 'CAM_Alt'
elif intype is 'px4_utc':
    latf = 'Lat'
    lonf = 'Lon'
    altf = 'Elev'
elif intype is 'flytrex':
    latf = 'latitude'
    lonf = 'longitude'
    altf = 'altitude_feet'
    alt_factor = 0.3048

#Convert Altitude to HAE
#Currently assumes the EGM96 geoid model is used
lat, lon, z = ra[latf].astype(float), ra[lonf].astype(float), ra[altf].astype(float)*alt_factor
newlon, newlat, newz = geolib.geoid2ell(lon, lat, z)

#Sanity check
print 'First input altitude change:'
print ra[altf][0]
print newz[0]

#Replace altitude values
ra[altf] = np.around(newz, 2)

#There is probably a better way to do this by updating dictionary key
#For now, assume clean input w/ alt in field 4
if altf is 'altitude_feet':
    names = list(ra.dtype.names)
    names[3] = 'altitude_m_hae'
    ra.dtype.names = names

#Replace datum tag - so we know what we've already updated
datumf = 'GPSMapDatum'
if datumf in ra.dtype.names:
    new_datum = str('WGS 84 HAE')
    ra[datumf] = new_datum 
#else:
    #Append datum field

#This is the only real option to save the recarray to csv
genlib.write_recarray(outfn, ra)

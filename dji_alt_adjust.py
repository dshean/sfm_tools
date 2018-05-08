#! /usr/bin/env python

"""
David Shean
dshean@gmail.com

This script will fix issues with EXIF Altitude geotags for images acquired with DJI Phantom
Necessary for standard SfM workflows with software that reads EXIF data (Agisoft PhotoScanPro, Pix4D)

The AbsoluteAltitude and GPSAltitude tags should be relative to mean sea level (MSL, using EGM96 geoid).
For whatever reason, with Phantom 3 Pro and Phantom 4 Pro, these values are way off, in some cases >100 m off
The error is way too large for typical GNSS vertical error, and is likely a DJI bug (sigh)
Forums suggest this is also an issue for DJI Inspire.  
This does not appear to be an issue with Mavic Pro.

The RelativeAltitude (using barometer) is a much more precise altitude relative to the home point (where RelativeAltitude is 0.0)
If we have a known absolute altitude for the home point (from GCPs or accurate AbsoluteAltitude), we can then use the RelativeAltitude values to update the AbsoluteAltitude for each image
This script creates a copy of original images ("modified" subdirectory), and updates the GPSAltitude tags

Modified from code here: http://forum.dev.dji.com/thread-31960-1-1.html

Requires PyExifTool
pip install ocrd-pyexiftool
"""

import os
import sys
import glob
import shutil

import exiftool

def display_image_altitude(fn_list):
    with exiftool.ExifTool() as et:
        for fn in fn_list:
            tags = ['EXIF:GPSAltitude', 'EXIF:GPSAltitudeRef', 'XMP:AbsoluteAltitude', 'XMP:RelativeAltitude']
            metadata = et.get_tags(tags, fn)
            gpsAlt = float(metadata['EXIF:GPSAltitude'])
            gpsAltRef = int(metadata['EXIF:GPSAltitudeRef'])
            absAlt = float(metadata['XMP:AbsoluteAltitude'])
            relAlt = float(metadata['XMP:RelativeAltitude'])
            print('{}   {:0.1f}   {:d}   {:0.1f}   {:0.1f}'.format(os.path.basename(fn), gpsAlt, gpsAltRef, absAlt, relAlt))

def update_gps_altitude(fn_list, home_alt_msl):
    with exiftool.ExifTool() as et:
        for fn in fn_list:
            tags = ['XMP:RelativeAltitude']
            metadata = et.get_tags(tags, fn)

            relAlt = float(metadata['XMP:RelativeAltitude'])
            adjAlt = home_alt_msl + relAlt
            etArg = ["-GPSAltitude=" + str(adjAlt),]
            #Set altitude reference
            #1 is 'Below Sea Level'; 0 is 'Above Sea Level'
            if adjAlt >= 0.0:
                etArg.append("-GPSAltitudeRef=0")
            else:
                etArg.append("-GPSAltitudeRef=1")
            #Since we're modifying our own copy of originl, we don't need the default exiftool _original copy
            etArg.append("-overwrite_original")
            print(etArg)
            #pyexiftool execution requires binary string
            etArg_b = [str.encode(a) for a in etArg]
            f_b = str.encode(fn)
            etArg_b.append(f_b)
            et.execute(*etArg_b)

#Input directory containing images
image_dir = '.'

#Altitude of home point, meters above WGS84 ellipsoid 
#This comes from GCP near home point
#Should extract automatically, see commented code below
home_alt_ell = -14.2

#Maintain consistence - absolute altitude relative to MSL
#Approx geoid offset in Seattle (note geoid is above ellipsoid)
geoid_height = -22.4
#Altitude of home point, meters above EGM96 geoid (mean sea level)
home_alt_msl = home_alt_ell - geoid_height

image_dir_mod = os.path.join(image_dir, 'modified')
if not os.path.exists(image_dir_mod):
    os.makedirs(image_dir_mod)

#Process both RAW and JPG
ext_list = ["DNG", "JPG"]
for ext in ext_list:
    fn_list_orig = glob.glob(os.path.join(image_dir, '*.%s' % ext))
    if fn_list_orig:
        print("\nProcessing %s files" % ext)
        print("Creating copy of all files")
        for fn in fn_list_orig:
            if (os.path.isfile(fn)):
                if not os.path.exists(os.path.join(image_dir_mod, fn)):
                    print(fn)
                    shutil.copy2(fn, image_dir_mod)

        fn_list_mod = glob.glob(os.path.join(image_dir_mod, '*.%s' % ext))

        #  Display the value of 'EXIF:GPSAltitude', 'EXIF:GPSAltitudeRef', 'XMP:AbsoluteAltitude','XMP:RelativeAltitude' metadata
        display_image_altitude(fn_list_orig)

        #  Updates EXIF:GPSAltitude to be the value of (XMP:RelativeAltitude + homePointAltitude)
        update_gps_altitude(fn_list_mod, home_alt_msl)

        #  Display the value of 'EXIF:GPSAltitude', 'EXIF:GPSAltitudeRef', 'XMP:AbsoluteAltitude','XMP:RelativeAltitude' metadata
        display_image_altitude(fn_list_mod)

"""
#Code to automatically extract MSL elevation for a given lat/lon
#Original code here: https://mavicpilots.com/threads/altitude-information-from-exif-data-photos.32535/

import urllib
import json
import exifread

# get degress from GPS EXIF tag
def degress(tag):
    d = float(tag.values[0].num) / float(tag.values[0].den)
    m = float(tag.values[1].num) / float(tag.values[1].den)
    s = float(tag.values[2].num) / float(tag.values[2].den)
    return d + (m / 60.0) + (s / 3600.0)

# must provide a file name
if (len(sys.argv)!=2):
    raise Exception("No file name provided")
filename = sys.argv[1]

# read the exif tags
with open(filename, 'rb') as f:
    tags = exifread.process_file(f)

# get lat/lon
lat = degress(tags["GPS GPSLatitude"])
lon = degress(tags["GPS GPSLongitude"])
lat = -lat if tags["GPS GPSLatitudeRef"].values[0]!='N' else lat
lon = -lon if tags["GPS GPSLatitudeRef"].values[0]!='E' else lon

# get ground elevation at this location, if possible
try:
    ground_level = float("nan")
    open_elevation_reply = json.loads(urllib.urlopen("https://api.open-elevation.com/api/v1/lookup?locations=%f,%f" % (lat,lon)).read())
    ground_level = float(open_elevation_reply["results"][0]["elevation"])
except:
    pass

# get the altitude
alt = tags["GPS GPSAltitude"]
alt = float(alt.values[0].num) / float(alt.values[0].den)
below_sea_level = tags["GPS GPSAltitudeRef"].values[0]!=0;
alt = -alt if below_sea_level else alt
agl = alt - ground_level

# spit it out
print("Latitude[deg]     : %f" % lat)
print("Longitude[deg]    : %f" % lon)
print("Altitude [m, ASL] : %f" % alt)
print("Altitude [m, AGL] : %f" % agl)
"""

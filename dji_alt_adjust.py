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

Should migrate to exifread instead of exiftool

#Code to automatically extract MSL elevation for a given lat/lon
#Original code here: https://mavicpilots.com/threads/altitude-information-from-exif-data-photos.32535/
"""

import os
import sys
import glob
import shutil

import urllib.request

import exiftool

#Start subprocess with exiftool
et = exiftool.ExifTool() 
et.start()

#Returns dictionary with relevant EXIF tags 
def get_metadata(fn, et=et):
    tags = ['EXIF:GPSLatitude', 'EXIF:GPSLongitude', 'EXIF:GPSLatitudeRef', 'EXIF:GPSLongitudeRef', \
            'EXIF:GPSAltitude', 'EXIF:GPSAltitudeRef', 'XMP:AbsoluteAltitude', 'XMP:RelativeAltitude']
    metadata = et.get_tags(tags, fn)
    #Convert to positive east longitude
    if metadata['EXIF:GPSLongitudeRef'] == "W":
        metadata['EXIF:GPSLongitude'] *= -1
    if metadata['EXIF:GPSLatitudeRef'] == "S":
        metadata['EXIF:GPSLatitude'] *= -1
    print(metadata)
    return metadata

#Get approximate elevation MSL from 10-m NED
def USGS10mElev(lon, lat):
    url = 'https://nationalmap.gov/epqs/pqs.php?x=%.8f&y=%.8f&units=Meters&output=xml' % (lon, lat)
    r = urllib.request.urlopen(url)
    out = None
    if r.status == 200:
        xml = r.read()
        print(xml)
        out = float(xml[xml.find(b'<Elevation>')+11:xml.find(b'</Elevation>')-1])
    print("USGS elevation MSL: %0.2f" % out)
    return out

#Global solution, not tested
#r = json.loads(urllib.urlopen("https://api.open-elevation.com/api/v1/lookup?locations=%f,%f" % (lat,lon)).read())
#out = float(r["results"][0]["elevation"])

def update_gps_altitude(fn, home_alt_msl=None):
    #tags = ['XMP:RelativeAltitude']
    #metadata = et.get_tags(tags, fn)
    metadata = get_metadata(fn)

    relAlt = float(metadata['XMP:RelativeAltitude'])

    #Only need to do this once 
    if home_alt_msl is None:
        home_alt_msl = USGS10mElev(metadata['EXIF:GPSLongitude'], metadata['EXIF:GPSLatitude'])
        
    adjAlt = home_alt_msl + relAlt
    etArg = ["-GPSAltitude=" + str(adjAlt),]
    etArg.append("-AbsoluteAltitude=" + str(adjAlt))
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
    metadata = get_metadata(fn)

#Input directory containing images
#image_dir = '.'
image_dir = sys.argv[1]

image_dir_mod = os.path.join(image_dir, 'modified')
if not os.path.exists(image_dir_mod):
    os.makedirs(image_dir_mod)

#Should accept as argument
#out_ref = "HAE"
out_ref = "MSL"

#Known altitude of home point, meters above WGS84 ellipsoid 
#This comes from GCP near home point
#Montlake Triangle
home_alt_ell = -1.0
#IMA fields
#home_alt_ell = -14.2
#Beach at sea level
#home_alt_ell = -22.7 
#Nooksack River Site
#home_alt_ell = 72 
#Baker
#home_alt_ell = 1642

#Approx geoid offset for Benchmark #533 on UW Campus in Seattle, relative to ellipsoid
#Note: geoid is below ellipsoid at this location
geoid_height = -23.75

home_alt_msl = None
if out_ref == "MSL":
    #If desired, output absolute altitude relative to MSL
    #Altitude of home point, meters above EGM96 geoid (mean sea level)
    home_alt_msl = home_alt_ell - geoid_height

#Process both RAW and JPG
#ext_list = ["DNG", "JPG", "jpg"]
ext_list = ["JPG", "jpg"]
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
        
        #Get list of files to modify
        fn_list_mod = glob.glob(os.path.join(image_dir_mod, '*.%s' % ext))

        #Only need to do this once for first image near home point
        metadata = get_metadata(fn_list_mod[0])
        if home_alt_msl is None:
            home_alt_msl = USGS10mElev(metadata['EXIF:GPSLongitude'], metadata['EXIF:GPSLatitude'])

        #Update EXIF:GPSAltitude to be the value of (XMP:RelativeAltitude + homePointAltitude)
        for fn in fn_list_mod:
            update_gps_altitude(fn, home_alt_msl)

et.terminate()

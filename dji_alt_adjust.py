#! /usr/bin/env python

"""
David Shean
dshean@gmail.com

This script will fix issues with EXIF Altitude geotags for images acquired with DJI Phantom
Necessary for standard SfM workflows with software that reads EXIF data (Agisoft PhotoScanPro, Pix4D)

The EXIF AbsoluteAltitude and GPSAltitude tags should be relative to mean sea level (MSL, using EGM96 geoid).

For whatever reason, with DJI platforms, these values are way off, in some cases >100 m off
The error is way too large for typical GNSS vertical error, and is likely a DJI bug (sigh)
Forums suggest this is also an issue for DJI Inspire.  
This was not issue with Mavic Pro during tests in 2018, but is an issue in 2019.

The RelativeAltitude (using barometer) is a much more precise altitude relative to the home point (where RelativeAltitude is 0.0)
If we have a known absolute altitude for the home point (from GCPs or accurate AbsoluteAltitude), we can then use the RelativeAltitude values to update the AbsoluteAltitude for each image
This script creates a copy of original images ("modified" subdirectory), and updates the GPSAltitude tags

Requires PyExifTool
pip install ocrd-pyexiftool

Should migrate to exifread instead of exiftool
"""

import os
import sys
import glob
import shutil
import argparse

import requests

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
def get_NED(lon, lat):
    url = 'https://nationalmap.gov/epqs/pqs.php?x=%.8f&y=%.8f&units=Meters&output=json' % (lon, lat)
    r = requests.get(url)
    out = None
    if r.status_code == 200:
        out = r.json()['USGS_Elevation_Point_Query_Service']['Elevation_Query']['Elevation']
    print("USGS elevation MSL: %0.2f" % out)
    return out

#Get approximate elevation MSL from Open Elevation API
def get_OpenElevation(lon, lat):
    url = 'https://api.open-elevation.com/api/v1/lookup?locations=%0.8f,%0.8f' % (lat, lon)
    r = requests.get(url)
    out = None
    if r.status_code == 200:
        out = r.json()['results'][0]['elevation']
    print("Open Elevation MSL: %0.2f" % out)
    return out

def get_MSL(lon,lat):
    out = get_NED(lon, lat)
    if out is None:
        out = get_OpenElevation(lon, lat)
    return out 

#https://www.ngs.noaa.gov/web_services/geoid.shtml
def get_GeoidOffset(lon, lat):
    #Can specify model, 13 = GEOID12B
    url = 'https://geodesy.noaa.gov/api/geoid/ght?lat=%0.8f&lon=%0.8f' % (lat, lon)
    r = requests.get(url)
    out = None
    if r.status_code == 200:
        out = r.json()['geoidHeight']
    print("NGS geoid offset: %0.2f" % out)
    return out

#Can also query UNAVCO geoid offset calculator

def update_gps_altitude(fn, home_elev):
    #tags = ['XMP:RelativeAltitude']
    #metadata = et.get_tags(tags, fn)
    metadata = get_metadata(fn)

    relAlt = float(metadata['XMP:RelativeAltitude'])
    adjAlt = home_elev + relAlt

    #Update metadata
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

    #Check updated
    metadata = get_metadata(fn)

def getparser():
    cwd = os.getcwd()
    parser = argparse.ArgumentParser(description="Update incorrect GPS altitude for images acquired with DJI platforms", \
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    #Could make this optional with cwd, but good to have check
    parser.add_argument('img_dir', type=str, default=cwd, help='Directory containing images')
    parser.add_argument('-out_dir', type=str, default=None, help='Output directory (default is "modified" subdirectory)')
    parser.add_argument('-ext_list', type=str, nargs='+', default=['JPG',], help='Process files with these extensions')
    parser.add_argument('-out_elev_ref', type=str, default='MSL', choices=['MSL', 'HAE'], help='Output elevation reference')
    parser.add_argument('-home_HAE', type=float, default=None, \
            help='Known home point elevation, meters height above ellipsoid')
    parser.add_argument('-home_MSL', type=float, default=None, \
            help='Known home point elevation, meters height above geoid (mean sea level)')
    parser.add_argument('-geoid_offset', type=float, default=None, \
            help='Known offset of geoid relative to ellipsoid (meters)') 
    return parser

#Known altitude of home point, meters above WGS84 ellipsoid 
#This comes from GCP near home point
#Montlake Triangle
#home_HAE = -1.0
#IMA fields
#home_HAE = -14.2
#Beach at sea level
#home_HAE = -22.7 
#Nooksack River Site
#home_HAE = 72 
#Baker
#home_HAE = 1642

#Approx geoid offset for Benchmark #533 on UW Campus in Seattle, relative to ellipsoid
#Note: geoid is below ellipsoid at this location
#geoid_offset = -23.75

def main(argv=None):
    parser = getparser()
    args = parser.parse_args()

    #Input directory containing images
    image_dir = args.img_dir

    if args.out_dir is not None:
        image_dir_mod = args.out_dir
    else:
        image_dir_mod = os.path.join(image_dir, 'modified')

    if not os.path.exists(image_dir_mod):
        os.makedirs(image_dir_mod)

    #This is the final reference elevation to use
    home_elev = None

    #Extract home point information - only need to do this once
    #Assume that first image, sorted alphanumerically, is near home point
    fn_list_orig = sorted(glob.glob(os.path.join(image_dir, '*.%s' % args.ext_list[0])))
    print('\nGetting metadata for first image (assumed to be near home point)')
    home_metadata = get_metadata(fn_list_orig[0])
    home_lon = home_metadata['EXIF:GPSLongitude']
    home_lat = home_metadata['EXIF:GPSLatitude']

    if args.out_elev_ref == 'MSL':
        #If input HAE is provided
        if args.home_HAE is not None:
            if args.geoid_offset is None:
                args.geoid_offset = get_GeoidOffset(home_lon, home_lat)
            args.home_MSL = args.home_HAE - args.geoid_offset
        else:
            if args.home_MSL is None:
                args.home_MSL = get_MSL(home_lon, home_lat)
        home_elev = args.home_MSL

    elif args.out_elev_ref == 'HAE':
        if args.home_HAE is None:
            if args.home_MSL is None:
                args.home_MSL = get_MSL(home_lon, home_lat)
            if args.geoid_offset is None:
                args.geoid_offset = get_GeoidOffset(home_lon, home_lat)
            args.home_HAE = args.home_MSL + args.geoid_offset
        home_elev = args.home_HAE

    print("Setting home point elevation to %0.2f m %s" % (home_elev, args.out_elev_ref))

    for ext in args.ext_list:
        fn_list_orig = sorted(glob.glob(os.path.join(image_dir, '*.%s' % ext)))
        print("\nProcessing %s files" % ext)
        print("Creating copy of all files")
        for fn in fn_list_orig:
            if (os.path.isfile(fn)):
                if not os.path.exists(os.path.join(image_dir_mod, fn)):
                    print(fn)
                    shutil.copy2(fn, image_dir_mod)

        #Get list of files to modify
        fn_list_mod = sorted(glob.glob(os.path.join(image_dir_mod, '*.%s' % ext)))
        #Update EXIF:GPSAltitude to be the value of (XMP:RelativeAltitude + homePointAltitude)
        for fn in fn_list_mod:
            update_gps_altitude(fn, home_elev)
    et.terminate()

if __name__ == "__main__":
    main()

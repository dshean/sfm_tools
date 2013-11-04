#! /bin/bash

#Input: shp from Trimble Pathfinder Office shp
shp_fn = $1
photo_dir = $2

#Convert to gpx
gpx_fn = ${shp_fn%%*.shp}.gpx
ogr2ogr -f GPX -dsco GPX_USE_EXTENSIONS=yes $gpx_fn $shp_fn

#Sync with exif timestamp and write interpolated GPS coord to exif header
geosync_offset = 0.0
exiftool -Geotag $gpx_fn -Geosync=$geosync_offset "-Geotime<SubSecDateTimeOriginal" $photo_dir

#exiftool -exif:GPSLatitude=$xyz[2] -exif:GPSLatitudeRef=$latref -exif:GPSLongitude=$xyz[1] -exif:GPSLongitudeRef=$lonref -exif:GPSAltitude=$xyz[3] -exif:GPSAltitudeRef\#=$altref $img

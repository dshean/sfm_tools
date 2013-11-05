#! /bin/bash

#David Shean
#dshean@gmail.com
#11/4/13

#Requires exiftool, gpsbabel, ogr/gdal

#Input should be csv output from Trimble Pathfinder Office
#"Configurable ascii"
#Positions only - One point per GPS position
#CSV template (note: NO {GPS Time}) 
#{Feature ID} {Latitude} {Longitude} {HAE} {Attributes}
#Check "use template as header"

#NOTE: Apparently, we need to use "Date recorded" and "Time recorded" output from TPO
#This was ~7 seconds earlier than the recorded GPS Time for each point in the 20130716 Greenland hike
#This syncs with the Nikon GP-1 GPS timestamps

in_fn=$1
photo_dir=$2

#Output original photo locations as shp
out=exif_coord_original
exif2shp.sh $photo_dir $out

#Convert to gpx
gpx_fn=${in_fn%%.*}.gpx
#ogr2ogr -f GPX -dsco GPX_USE_EXTENSIONS=yes $gpx_fn $shp_fn

#Convert TPO to gpx track
echo "Converting $in_fn to $gpx_fn"
#Assuming TPO output (csv) has header with standard field names, the following will work 
#utc=0 is required to set GPS time zone to UTC, not local time zone
#-t creates a track instead of waypoints
gpsbabel -t -i unicsv,utc=0 -f $in_fn -o GPX -F $gpx_fn

echo "Updating geotagging in $photo_dir"

#Timezone offset of exif DateTimeOriginal relative to UTC
#This is the value for Greenland 2013 images (doh!)
#Should be 0 when camera clock is set to UTC
tz="-02:00"

#This is the offset between the camera clock and GeoXH GPS time, should only be a few seconds
geosync_offset=0.0

#Could also use this, but not all images have valid GPS info from Nikon GP-1
#"-Geotime<GPSDateTime"
#The exiftool doc describes a way to use certain photos as tiepoints for -Geosync
#Should be able to script this to use all available exif GPS times

#Use Original DateTime with Subsecond (precision 0.1 s for D800) time in exif header
exiftool -progress -Geotag $gpx_fn -Geosync=$geosync_offset "-Geotime<\${SubSecDateTimeOriginal}${tz}" $photo_dir

#Move original jpg to subfolder
mkdir $photo_dir/jpg_original
mv $photo_dir/*.jpg_original $photo_dir/jpg_original

#Output corrected photo locations as shp
out=exif_coord_corrected
exif2shp.sh $photo_dir $out

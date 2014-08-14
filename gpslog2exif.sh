#! /bin/bash

#David Shean
#dshean@gmail.com
#11/4/13

#Use csv or gpx GPS log from to geotag a directory full of photos
#Requires exiftool, gpsbabel, ogr/gdal
#Must set offsets manually

#Need to prevent GPSMapDatum from being updated when geotagging with TPO GPS log doesn't occur (no overlap)

#Tested with input csv from Trimble Pathfinder Office
#Use preset csv_geoxh_ptlog
#"Configurable ascii"
#Positions only - One point per GPS position
#CSV template (note: NO {GPS Time}) 
#{Feature ID} {Latitude} {Longitude} {HAE} {Attributes}
#Check "use template as header"

#NOTE: Apparently, we need to use "Date recorded" and "Time recorded" output from TPO
#This was ~7 seconds earlier than the recorded GPS Time for each point in the 20130716 Greenland hike
#This syncs with the Nikon GP-1 GPS timestamps
exif2shp=/Users/dshean/src/sfm/exif2gpslog.sh

echo
if [ $# -ne 2 ] ; then
     echo "Usage is $0 tpo.[csv,gpx] photodir"
     echo
     exit 1
fi

in_fn=$1
photo_dir=$2

#Copy the TPO csv to photo directory as a record
rsync -av $in_fn $photo_dir

#Timezone offset of exif DateTimeOriginal relative to UTC
#Should be 0 when camera clock is properly set to UTC (with daylight savings off)
tz="-00:00"
#This is the value needed for Greenland 2013 images (doh!)
#tz="-02:00"
#For 20130509 flight 
#tz="-07:00"

#This is the offset between the camera clock and GeoXH GPS time, should only be a few seconds
#From exiftool doc:
#This time difference may be of the form "SS", "MM:SS", "HH:MM:SS" or "DD HH:MM:SS" (where SS=seconds, MM=minutes, HH=hours and DD=days), and a leading "+" or "-" may be added for positive or negative differences (negative if the camera clock was ahead of GPS time). Fractional seconds are allowed (eg. "SS.ss").
geosync_offset=0.0
#20130509 Rainier flight
#geosync_offset=+0.5
#201207 fieldwork
#geosync_offset=+3.0
#20140808 baker NEX-5 UAV flights
#geosync_offset=-1.0

#Use SubSec times if they are available
firstphoto=$(ls $photo_dir | head -1)
if [[ -n $(exiftool -SubSecTimeOriginal $firstphoto) ]]; then
    subsec=true
else
    subsec=false
fi

#Output original photo locations as shp
#Note: this will update GPSAltitude to HAE if not already done
if [ "$(exiftool -GPSLatitude $photo_dir | grep 'GPS' | wc -l)" -gt "2" ]; then
    echo "Generating shp from original photo exif data"
    out=exif_coord_original
    echo $exif2shp $photo_dir $out
    $exif2shp $photo_dir $out
fi

#Convert TPO csv gps log to gpx (currently required by exiftool)
gpx_fn=${in_fn%.*}.gpx
if [ ! -e $gpx_fn ] ; then
    #ogr2ogr -f GPX -dsco GPX_USE_EXTENSIONS=yes $gpx_fn $shp_fn
    echo "Converting $in_fn to $gpx_fn"
    #Assuming TPO output (csv) has header with standard field names, the following will work 
    #utc=0 is required to set GPS time zone to UTC, not local time zone
    #-t creates a track instead of waypoints
    gpsbabel -t -i unicsv,utc=0 -f $in_fn -o GPX -F $gpx_fn
fi

echo
echo "Updating geotagging in $photo_dir (and updating GPSMapDatum, which requires backup)"

#Want to update the datum, since TPO positions are all HAE
#Need some way to only do this for images that are actually geotagged here

#Note: when gpx log times don't overlap, this gives
#   Warning: No writable tags set from ./DSC_9460.NEF

#Use Original DateTime with Subsecond (precision 0.1 s for D800) time in exif header
if $subsec ; then
    exiftool -progress -fileOrder DateTimeOriginal -Geotag $gpx_fn -Geosync=$geosync_offset "-Geotime<\${SubSecDateTimeOriginal}${tz}" -GPSMapDatum='WGS 84 HAE' $photo_dir
else
    exiftool -progress -fileOrder DateTimeOriginal -Geotag $gpx_fn -Geosync=$geosync_offset "-Geotime<\${DateTimeOriginal}${tz}" -GPSMapDatum='WGS 84 HAE' $photo_dir
fi

#Could also use GPSDateTime, but not all images have valid GPS info from Nikon GP-1
#"-Geotime<GPSDateTime"
#The exiftool doc describes a way to use certain photos as tiepoints for -Geosync
#Should be able to script this to use all available exif GPS times

#Move original jpg to subfolder
#mkdir $photo_dir/original
#mv $photo_dir/*.*_original $photo_dir/original

#Output corrected photo locations as shp
echo
echo "Generating shp from updated photo exif data"
out=exif_coord_corrected
echo $exif2shp $photo_dir $out
$exif2shp $photo_dir $out

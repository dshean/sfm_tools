#! /bin/bash

#David Shean
#dshean@gmail.com
#11/4/13

#This is will generate a shapefile using EXIF gps tags for photos in input directory
#Requires ExifTool and GDAL/OGR

#!!!
#NOTE: Nikon GP-1 GPS altitude is MSL, not WGS84 ellipsoid
#Need to write HAE altitude back to original images
#run exif_gpsalt_msl2hae.sh dir first
#!!!

#Nikon GP-1 accuracy is 10 m RMS (as stated in manual), assumed to be horizontal
#Print UTC and local time, can use $Timezone tag

#See http://www.sno.phy.queensu.ca/~phil/exiftool/geotag.html

echo
if [ $# -ne 2 ] ; then
    echo "Usage is $0 photodir outname"
    echo
    exit 1
fi

dir=$1
out=${2%.*}

#Correct GPSAltitude from MSL to HAE
msl2hae=true
if $msl2hae ; then
    echo "Correcting GPSAltitude from MSL to HAE"
    #Note: this script contains a check to see if tags have already been corrected
    exif_msl2hae.sh $dir
    echo
fi

#fmt=/Users/dshean/src/sfm/gpx.fmt
#fmt=/Users/dshean/src/sfm/kml.fmt
#exiftool -r -if '$gpsdatetime' -fileOrder gpsdatetime -p $fmt -d %Y-%m-%dT%H:%M:%SZ $dir/*.JPG > out.gpx

#-m ignores minor warnings and prints empty values to csv field
#-r is recursive
#-c is coordinate format, + for signed, decimal degrees
#-n will force numerical output for all tags (could be used instead of -c above)
#The # after a tag forces numerical output
#-if conditionally processes input

#Define exiftool tags to be extracted
#For some reason, the GPSAltitude tag is integer in output
fmt_str='$FileName,$DateTimeOriginal,$SubSecDateTimeOriginal,$GPSDateTime,$GPSLatitude#,$GPSLongitude#,$GPSAltitude#,$GPSMapDatum,$LensID,$FocalLength#,$ShutterSpeed,$Aperture,$ISO,$FOV'

#Extract EXIF data to csv file
#exiftool -progress -m -r -c '%.6f' -p "$fmt_str" $dir/*.JPG 
echo "Extracting GPS info for shp"
echo $fmt_str | sed -e 's/\$//g' -e 's/\#//g' > $out.csv
#Limit to specific extension (useful when raw and jpg in same directory)
#exiftool -progress -if '$GPSDateTime' -fileOrder GPSDateTime -m -r -ext $ext -p "$fmt_str" $dir >> $out.csv 
echo exiftool -progress -if '$GPSDateTime' -fileOrder DateTimeOriginal -m -p "$fmt_str" $dir 
exiftool -progress -if '$GPSDateTime' -fileOrder DateTimeOriginal -m -p "$fmt_str" $dir >> $out.csv 

#Write out vrt for csv
echo -n > $out.vrt
echo '<OGRVRTDataSource>' >> $out.vrt
echo "      <OGRVRTLayer name=\"$out\">" >> $out.vrt
echo "         <SrcDataSource>$out.csv</SrcDataSource>" >> $out.vrt
echo '         <GeometryType>wkbPoint25D</GeometryType>' >> $out.vrt
echo '         <LayerSRS>EPSG:4326</LayerSRS>' >> $out.vrt
echo '         <GeometryField encoding="PointFromColumns" x="GPSLongitude" y="GPSLatitude" z="GPSAltitude"/>' >> $out.vrt
echo '      </OGRVRTLayer>' >> $out.vrt
echo '</OGRVRTDataSource>' >> $out.vrt

#Convert to ESRI Shapefile
echo
echo "Creating shp from vrt"
echo ogr2ogr -overwrite $out.shp $out.vrt
ogr2ogr -overwrite -nln $out $out.shp $out.vrt

#ogr2ogr -f GPX -dsco GPX_USE_EXTENSIONS=YES out.gpx out.vrt

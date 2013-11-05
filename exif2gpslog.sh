#! /bin/bash

#David Shean
#dshean@gmail.com
#11/4/13

#NOTE: Nikon GP-1 GPS altitude is MSL, not WGS84 ellipsoid
#Nikon GP-1 accuracy is 10 m RMS (as stated in manual), assumed to be horizontal
#Print UTC and local time, can use $Timezone tag

#See http://www.sno.phy.queensu.ca/~phil/exiftool/geotag.html

#dir=$(pwd)
dir=$1
out=$2

#fmt=/Users/dshean/src/sfm/gpx.fmt
#fmt=/Users/dshean/src/sfm/kml.fmt
#exiftool -r -if '$gpsdatetime' -fileOrder gpsdatetime -p $fmt -d %Y-%m-%dT%H:%M:%SZ $dir/*.JPG > out.gpx

#-m ignores minor warnings and prints empty values to csv field
#-r is recursive
#-c is coordinate format, + for signed, decimal degrees
#-n will force numerical output for all tags (could be used instead of -c above)
#The # after a tag forces numerical output
#-if conditionally processes input

fmt_str='$FileName, $SubSecDateTimeOriginal, $GPSDateTime, $GPSLatitude#, $GPSLongitude#, $GPSAltitude#, $LensID, $FocalLength#, $ShutterSpeed, $Aperture, $ISO, $FOV, $FocusDistance, $DOF'

#exiftool -progress -m -r -c '%.6f' -p "$fmt_str" $dir/*.JPG 
echo $fmt_str > $out.csv
exiftool -progress -if '$GPSDateTime' -fileOrder GPSDateTime -m -r -ext JPG -p "$fmt_str" $dir >> $out.csv 

#Write out vrt for csv
echo -n > $out.vrt
echo '<OGRVRTDataSource>' >> $out.vrt
echo "      <OGRVRTLayer name=\"$out\">" >> $out.vrt
echo "         <SrcDataSource>$out.csv</SrcDataSource>" >> $out.vrt
echo '         <GeometryType>wkbPoint25D</GeometryType>' >> $out.vrt
echo '         <LayerSRS>EPSG:4326</LayerSRS>' >> $out.vrt
echo '         <GeometryField encoding="PointFromColumns" x="$GPSLongitude#" y="$GPSLatitude#" z="$GPSAltitude#"/>' >> $out.vrt
echo '      </OGRVRTLayer>' >> $out.vrt
echo '</OGRVRTDataSource>' >> $out.vrt

#Convert to ESRI Shapefile
ogr2ogr -overwrite $out.shp $out.vrt

#ogr2ogr -f GPX -dsco GPX_USE_EXTENSIONS=YES out.gpx out.vrt

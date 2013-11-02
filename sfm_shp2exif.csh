#! /bin/tcsh -f

#NOTE 7/27/13
#See http://www.sno.phy.queensu.ca/~phil/exiftool/geotag.html
#Good information about tagging photos w/ GPS tracklog

#This script will assign lat/lon/elev from a shapefile to exif data of photos
#It is assumed that the points are in the same order as the sfm site IDs, 

#Should really do this in python 

#For future SfM surveys, fully-automated pipeline
#With automatic geotagging from GPS log, can use spatial info to break into sites, or just lump everything together
#Can automatically process files based on time, break into sites, extract focal length

#exiftool can automatically geotag photos given an input GPS log - need some way to go from GeoXH 

#set photodir = ~/Documents/UW/MtRainier/2012_Field_Data/Paradise/SfM/Nisqually_vista
#set shpfile = ~/Documents/UW/MtRainier/2012_Field_Data/Paradise/shp/20120706_shean_rainier_nisqually.shp

#set echo

set photodir = $1
set shpfile = $2

#set exiftool = '/Volumes/dshean/sw/Image-ExifTool-8.97/exiftool'
set exiftool = '~/sw/Image-ExifTool-8.97/exiftool'

cd $photodir

set photodirlist = (`ls -d * | grep 'sfm' `) 

echo
foreach i ($photodirlist)
echo $i
set sitenum = `echo $i | cut -c 14-15`
#Point features are 0-relative
@ sitenum--
#set sitenum = `printf '%02i' $sitenum`

#Need to deal with features that have multiple attributes

#Sunrise
#grep statement must account for comment field
#set xyz = (`ogrinfo -al $shpfile | grep -A 2 ":$sitenum" | sed -e '1,2d' -e 's/[()]//g' -e 's/ POINT //' -e 's/^ //'`)

#Nisqually - no comment
set xyz = (`ogrinfo -al $shpfile | grep -A 1 ":${sitenum}"$ | grep POINT | sed -e 's/[()]//g' -e 's/ POINT //' -e 's/^ //'`)
echo $xyz

set latref = 'N'
if (`echo "a=($xyz[2] < 0); a" | bc -l`) then
    set latref = 'S'
endif

set lonref = 'E'
if (`echo "a=($xyz[1] < 0); a" | bc -l`) then
    set lonref = 'W'
    set xyz[1] = `echo $xyz[1] | sed 's/-//'`
endif

set altref = 0
if (`echo "a=($xyz[3] < 0); a" | bc -l`) then
    set altref = 1
endif

ls $photodir/$i
set imglist = (`ls $photodir/$i/*/*.jpg`)

foreach img ($imglist)
echo $img
#Note, the #= turns off conversion and forces a uint8 value of 0 for "Above Sea Level"
$exiftool -exif:GPSLatitude=$xyz[2] -exif:GPSLatitudeRef=$latref -exif:GPSLongitude=$xyz[1] -exif:GPSLongitudeRef=$lonref -exif:GPSAltitude=$xyz[3] -exif:GPSAltitudeRef\#=$altref $img 
end
end

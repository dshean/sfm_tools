#! /bin/bash

#David Shean
#dshean@gmail.com
#8/13/14

#This will replace the default MSL GPSAltitude with HAE GPSAltitude for all photos in input directory 
#Requires ExifTool and GDAL/OGR

echo
if [ $# -eq 0 ] ; then
    echo "No input directory specified"
    exit 1
fi

dir=$1

#-m ignores minor warnings and prints empty values to csv field
#-r is recursive
#The # after a tag forces numerical output
#-if conditionally processes input

#Define exiftool tags to be extracted
fmt_str='$FileName,$GPSLatitude#,$GPSLongitude#,$GPSAltitude#,$GPSMapDatum'

#Extract EXIF data to csv file
echo "Generating csv of existing MSL GPSAltitude tags"
out=temp.csv
echo $fmt_str | sed -e 's/\$//g' -e 's/\#//g' -e 's/FileName/SourceFile/' > $out 
#exiftool -progress -if '$GPSAltitude' -m -r -p "$fmt_str" $dir >> $out 
#-if here checks to see if datum has already been updated with 'WGS 84 HAE' tag
echo exiftool -progress -fileOrder DateTimeOriginal -if '$GPSMapDatum ne "WGS 84 HAE"' -m -p "$fmt_str" $dir 
exiftool -progress -fileOrder DateTimeOriginal -if '$GPSMapDatum ne "WGS 84 HAE"' -m -p "$fmt_str" $dir >> $out

if [ "$(cat $out | wc -l)" -gt "1" ] ; then
    out=exif_gps_orig.csv
    mv temp.csv $out
    echo
    echo "Generated new csv with HAE GPSAltitude tags"
    exif_gpsalt_msl2hae_csv.py $out
    out_hae=${out%.*}_hae.csv
    #Isolate only tags to be updated (offers speedup?)
    cat $out_hae | awk 'BEGIN {FS=","; OFS=","} {print $1,$4,$5}' > temp.csv
    mv temp.csv $out_hae
    #Note: this creates a backup copy of the file, which takes forever for ~40-70MB D800 NEF
    echo
    echo "Updating original files with HAE GPSAltitude tags (creates backup copies = slow)"
    exiftool -progress -fileOrder DateTimeOriginal -csv=$out_hae -m $dir
else
    rm $out
fi

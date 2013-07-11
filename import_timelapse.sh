#! /bin/bash

name=20130710_timelapse_icebergs

srcdir='/Volumes/NO\ NAME/DCIM/10*NIKON'
dstdir=/Users/dshean/Documents/UW/Greenland/LakesRegion/2013_fieldseason/Illulisat_tests/$name

eval rsync -av $srcdir/*JPG $dstdir

for i in $dstdir/*JPG
do
if [ ! -e ${i%.*}_rot.jpg ] ; then 
    echo "rotating $i"
    convert -quality 90 -rotate 180 $i ${i%.*}_rot.jpg
fi
done

#Extract start number from ls
sn=$(ls $dstdir/*rot.jpg | head -1 | awk -F'/' '{print $NF}' | cut -c 5-8)
echo $sn

#ffmpeg -r 10 -force_fps -qscale 1 -an -y -start_number 012 -i DSCN0%03d.JPG $name.mp4
ffmpeg -r 10 -force_fps -qscale 1 -an -y -start_number $sn -i DSCN%04d_rot.jpg $dstdir/$name.mp4

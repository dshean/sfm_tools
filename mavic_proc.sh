#! /bin/bash

#MicroSD card
mavicdir=/Volumes/NO\ NAME/DCIM/100MEDIA
#Output directory
topdir=/Volumes/SHEAN_1TB_SSD
#Name of survey
dir=NisquallyRiver_SunshinePoint_Mavic_20170802

cd $topdir
if [ ! -e $dir ] ; then
    mkdir $dir
fi
cd $dir

#This will sync everything, should limit to new
rsync -av $mavicdir/ .

mkdir jpg; mv *JPG jpg/
mkdir dng; mv *DNG dng/
mkdir mp4; mv *MP4 mp4/

#Open Lightroom
#Import all DNG
#Adjust exposure if necessary
#Export with Mavic settings

#Need to modify GPS Altitude values
#dji_relalt2hae.sh

#Agisoft or Pix4D

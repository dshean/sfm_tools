#! /bin/bash 

#Want to use GNU parallel or xargs here instead of for loops

#Note, need to deal with incrementing 100ND800 to 101ND800 for single session

srcdir=/Volumes/Untitled/DCIM/100ND800
#dstdir=/Users/dshean/Pictures/20130330_DeceptionPass
dstdir=/Volumes/ESS_STF_1TB/dshean/20130509_D800_CVOflight_MSH_Rainier

#rsync *NEF
cd $dstdir

#For now, do this, eventually, want script to process individual photos, separate to batch
#Parallel thumbnail extraction
#parallel dcraw -e ::: *NEF

#Group by lens
#Preprocessing script that creates list, and creates subdirectories

for i in *NEF
do 
lens=$(exiftool -LensSpec $i | awk -F':' '{print $NF}' | sed -e 's/ //g' -e 's%/%%g')
fl=$(exiftool -FocalLength $i | awk -F':' '{print $NF}' | awk '{print $1}')
echo $i $lens $fl
done

#Write out lists with filenames for each lens
#Separated by time/position?  

exit

#for i in *NEF
#do
#echo $i
#echo "Extracting thumbnail"
#Use ufraw - Nikon tone curves
#ufraw-batch --embedded-image $i
#echo "Converting RAW to jpg"
ufraw_opt='--wb=camera --exposure=auto --out-type=jpg --compression=96 --color-smoothing'
parallel ufraw-batch $ufraw_opt ::: *NEF
#echo
#done

exit

dcraw_opt='-q 3 -T'
#Note - this is single-threaded, should use parallel here instead of for loop
#for i in *.NEF
for i in DSC_0137.NEF
do
echo $i
#Extract embedded thumbnails
echo "Extracting thumbnail"
dcraw -e $i
echo "Converting RAW to tif"
dcraw $dcraw_opt $i
echo "Converting tif to jpg"
convert -quiet -quality 90 ${i%.*}.tiff ${i%.*}.jpg
#rm ${i%.*}.tiff
echo
done

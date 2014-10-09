#! /bin/bash

fn_list=$(ls *[0-9].csv)

for i in $fn_list 
do
    flytrex2gpslog.sh $i
    gps_msl2hae_csv.py ${i%.*}_clean.csv
done

#Merge
ltype=clean_hae
merge_fn=merge_${ltype}
csv_list=($(ls *${ltype}.csv))
cat ${csv_list[@]} | sort -n | sed "1,$((${#csv_list[@]} - 1))d" > ${merge_fn}.csv
csv2vrt.py ${merge_fn}.csv
ogr2ogr -overwrite -nln $merge_fn ${merge_fn}.shp ${merge_fn}.vrt
gpx_list=($(ls *${ltype}.gpx))
str=''
for i in ${gpx_list[@]}
do
   str+="-f $i "
done
gpsbabel -t -i gpx $str -x track,merge,discard -o gpx -F ${merge_fn}.gpx

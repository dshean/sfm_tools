#! /bin/bash

#David Shean
#dshean@gmail.com
#7/31/14

#Utility to download and convert logs on Pixhawk SD Card

#sd_logdir='/Volumes/NO NAME/APM/LOGS'
sd_logdir='/Volumes/SHEAN_PX4/APM/LOGS'
out_logdir='/Users/dshean/Documents/UW/MtBaker/PX4'

dump=/Users/dshean/src/sfm/sdlog2_dump.py

if [ ! -d $out_logdir ] ; then
    mkdir -pv $out_logdir
fi

#Note: need to extract initialization time for PX4 - all times in log are relative
ts_fmt='%Y%m%d_%H%M%S'
#ts_fmt='%Y%m%d_%H%M'

#log_list=$(gls -1v "$sd_logdir"/*.BIN | tail -1)
log_list=$(gls -1v "$sd_logdir"/*.BIN)

#Want to rename
for log in $log_list
do
    echo $log
    bn=$(basename $log)
    #Get birth time
    ts=$(stat -f '%SB' -t $ts_fmt $log)
    #Get last modified time
    #ts=$(stat -f '%Sa' -t $ts_fmt $log)
    out_fn=$out_logdir/${ts}_${bn%.*}
    rsync -av $log ${out_fn}.bin
    #Dump entire log to ascii
    if [ ! -e ${out_fn}.log ] ; then 
        echo "Dumping entire log to ascii"
        $dump $log -v > ${out_fn}.log
    fi
    #Dump only GPS/ATT information
    #echo $dump $log -m CAM > ${out_fn%.*}_GPS_ATT.log
    if [ ! -e ${out_fn}_GPS_ATT.csv ] ; then 
        echo "Dumping GPS/ATT to csv"
        #$dump $log -m GPS -m ATT > ${out_fn}_GPS_ATT.csv
        #Want to delete first GPS line - always 0,0
        #Throw out entries with bad PDOP, usually 99.99
        $dump $log -m GPS -m ATT -m CAM | sed '2d' | awk 'BEGIN {FS=","; OFS=","} {if($5 < 12.0) print}' > ${out_fn}_GPS_ATT.csv
    fi
    #Convert to GPX
    #Convert to shp
    #Convert to kml
done

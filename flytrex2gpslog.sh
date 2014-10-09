#! /bin/bash

#David Shean
#10/8/14
#dshean@gmail.com

#Utility to clean up FlyTrex GPS log in preparation for geotagging photos

fn=$1

#latitude,longitude,altitude(feet),ascent(feet),speed(mph),distance(feet),max_altitude(feet),max_ascent(feet),max_speed(mph),max_distance(feet),time(millisecond),datetime(utc),datetime(local),satellites,pressure(Pa),temperature(F)

out_fn=${fn%.*}_clean.csv

#utc,lat,lon,alt,nsat
#Note: cut does not respect field order
#cut -d',' -f 12,1,2,3,14 $fn > $out_fn
awk 'BEGIN {FS=","; OFS=","} {print $12,$1,$2,$3,$14}' $fn | sed 's/ /T/' > $out_fn

#Scrub field names containing parenthesis
head -1 $out_fn | sed -e 's/(/_/g' -e 's/)//g' > temp
sed '1d' $out_fn >> temp
mv temp $out_fn

#Filter by number of satellites
nsat_fltr=true
min_nsat=5
if $nsat_fltr ; then
    #head -1 $out_fn > temp
    awk 'BEGIN {FS=","; OFS=","} {if( $5 >= '$min_nsat' ) print}' $out_fn >> temp
    mv $out_fn ${out_fn%.*}_orig.csv
    mv temp $out_fn
fi

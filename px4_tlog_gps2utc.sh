#! /bin/bash

#David Shean
#dshean@gmail.com
#8/10/14

#This formats the time and gps info from a PX4 telemetry log (tlog)

#tlog
#2014-08-08T20:46:55.860,FE,1E,A4, 1, 1,18,mavlink_gps_raw_int_t,time_usec,114150000,lat,487368470,lon,-1218404915,alt,1753700,eph,439,epv,65535,vel,2,cog,0,fix_type,3,satellites_visible,6,,Len,38
#fn=2014-08-08_13-46-36.csv

fn=$1
outfn=${fn%.*}_utc.csv
gpxfn=${fn%.*}_utc.gpx

echo 'DateTime,Lat,Lon,Elev' > $outfn

#Values are int in tlog
#Want to throw out anomalous 0,0,0 points - this is a hack
cat $fn | grep mavlink_gps_raw_int_t | 
awk 'BEGIN {FS=","; OFS=","} {printf "%s,%0.7f,%0.7f,%0.2f\n",$1, $12/1E7, $14/1E7, $16/1E3}' | 
grep -v '0.0000000,0.0000000,0.00' >> $outfn

gpsbabel -t -i unicsv,utc=0 -f $outfn -x track,merge,discard -o GPX -F $gpxfn

#Note: want to set exiftool to limit GeoMaxExtSecs in ~/.ExifTool_config
#This prevents photos taken before/after the GPS tracklog from being assigned positions
#exiftool -progress -Geotag $gpxfn -Geosync=-1.0 "-Geotime<\${DateTimeOrigial}-00:00" export_orig

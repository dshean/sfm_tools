#! /usr/bin/env python

#David Shean
#dshean@gmail.com
#8/9/14

#This takes a PX4 GPS/ATT log and spits out a csv w/ UTC,lat,lon,z for geotagging

import sys
import os
from datetime import datetime

import numpy as np
import gpstime

#GPS_Status,GPS_TimeMS,GPS_Week,GPS_NSats,GPS_HDop,GPS_Lat,GPS_Lng,GPS_RelAlt,GPS_Alt,GPS_Spd,GPS_GCrs,GPS_VZ,GPS_T,ATT_TimeMS,ATT_DesRoll,ATT_Roll,ATT_DesPitch,ATT_Pitch,ATT_DesYaw,ATT_Yaw
#3,513556400,1804,8,1.88,48.7367938,-121.8405264,-13.48,1743.93,0.04,180.38,0.129999995232,93040,93220,0.0,-1.19,0.0,0.77,4.9,4.9

in_fn = sys.argv[1]
out_fn = os.path.splitext(in_fn)[0]+'_utc.csv'
x = np.genfromtxt(in_fn, delimiter=',', names=True)

#Deal with fact that field names are different for GPS and CAM records: 'GPS_Week' vs 'CAM_GPSWeek'
if any('CAM' in s for s in x.dtype.names):
    week = 'CAM_GPSWeek'
    time = 'CAM_GPSTime'
    lat = 'CAM_Lat'
    lon = 'CAM_Lng'
    alt = 'CAM_Alt'
else:
    week = 'GPS_Week'
    time = 'GPS_TimeMS'
    lat = 'GPS_Lat'
    lon = 'GPS_Lng'
    alt = 'GPS_Alt'
    
#Note: Need to fix gpstime UTCFromGps function to work with np arrays
utc = [gpstime.UTCFromGps(z[0], z[1]) for z in zip(x[week], x[time]/1000.)]
#Note: gpsbabel needs the ISO format, otherwise can't handle sub-second
utc_dt = np.array([datetime(*t).isoformat() for t in utc])
y = np.array([utc_dt, x[lat], x[lon], x[alt]])

hdr = 'DateTime,Lat,Lon,Elev'
#np.savetxt(out_fn, y.T, delimiter=',', fmt='%s,%0.8f,%0.8f,%0.2f', header=hdr, comments='')
np.savetxt(out_fn, y.T, delimiter=',', fmt='%s', header=hdr, comments='')

#For tlog
#2014-08-08T20:46:55.860,FE,1E,A4, 1, 1,18,mavlink_gps_raw_int_t,time_usec,114150000,lat,487368470,lon,-1218404915,alt,1753700,eph,439,epv,65535,vel,2,cog,0,fix_type,3,satellites_visible,6,,Len,38
#fn=2014-08-08_13-46-36.csv
#outfn=${fn%.*}_utc.csv
#gpxfn=${fn%.*}_utc.gpx
#echo 'DateTime,Lat,Lon,Elev' > $outfn
#cat $fn | grep mavlink_gps_raw_int_t | awk 'BEGIN {FS=","; OFS=","} {printf "%s,%0.7f,%0.7f,%0.2f\n",$1, $12/1E7, $14/1E7, $16/1E3}' | grep -v '0.0000000,0.0000000,0.00' >> $outfn
#gpsbabel -t -i unicsv,utc=0 -f $outfn -x track,merge,discard -o GPX -F $gpxfn

#Note: want to set exiftool to limit GeoMaxExtSecs in ~/.ExifTool_config
#This prevents photos taken before/after the GPS tracklog from being assigned positions
#exiftool -progress -Geotag ~/Documents/UW/MtBaker/20140808_uav/PX4/merge.gpx -Geosync=-1.0 "-Geotime<\${DateTimeOrigial}-00:00" export_highcontrast



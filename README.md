# sfm_tools
A collection of tools to geotag and process photos for Structure from Motion (SfM)

## Most useful/mature tools:
* `cam_comparison_planning.py` - comparison of different cameras at different altitudes (FOV, pixel ground resolution, etc.)
* `agisoft_all.py` - automated Agisoft PhotoScanPro workflow using Agisoft Python API (written for older version, not tested with recent releases)
* `exif2gpslog.sh` - read EXIF data for a directory of photos and generate GPS log (csv, shp, or gpx)
* `exif_msl2hae.sh` and `gps_msl2hae_csv.py` - convert between default EXIF height above geoid (MSL, mean sea level) to height above ellipsoid (WGS84)
* `gpslog2exif.sh` - update EXIF positions based one external GPS log (e.g., log from Pixhawk4/Flytrex)
* Tools to pull GPS positions from Pixhawk4/Flytrex/Solo data logs, convert GPS week/seconds to UTC, etc.

## Dependencies:
* Several scripts rely on Phil Harvey's excellent [exiftool](http://www.sno.phy.queensu.ca/~phil/exiftool/)
* Output gpx currently uses [gpsbabel](http://www.gpsbabel.org/)
* Some shell scripts require [GDAL/OGR](http://www.gdal.org/) command line tools
* Some Python tools require numpy, matplotlib, and other python libraries (e.g., [pygeotools](https://github.com/dshean/pygeotools))

## Disclaimer:
Most of these were written for one-time projects with my UAV/camera hardware, which has evolved since 2013.  Many scripts still include hardcoded paths.  There are likely cleaner, more elegant ways to do much of this by now.  These days, many commercial UAV options/apps (e.g. DJI platforms, SenseFly platforms, 3DR SiteScan) will do much of this automatically.

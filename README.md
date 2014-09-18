sfm
===
A collection of tools to geotag and process photos for Structure from Motion (SfM)

* Tools to read GPS log and write to photo EXIF data
* Tools to read photo EXIF data and generate GPS log
* Tools to pull GPS positions from Pixhawk4 data logs, convert GPS week/seconds to UTC
* Tools to compute FOV, pixel ground resolution, etc. for different cameras at different altitudes
* Agisoft script is a sample of the complete Agisoft workflow using Agisoft Python API

Dependencies:
* Several scripts rely on Phil Harvey's excellent exiftool (http://www.sno.phy.queensu.ca/~phil/exiftool/)
* csv to gpx conversion currently uses gpsbabel (http://www.gpsbabel.org/)
* Some shell scripts require GDAL/OGR command line tools (http://www.gdal.org/)
* Some python tools require numpy, matplotlib and other python libraries in dshean/demtools

David Shean

dshean@gmail.com

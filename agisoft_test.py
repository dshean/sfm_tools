#! /usr/bin/env python

#David Shean
#dshean@gmail.com
#8/22/14

#Script for Agisoft PhotoScanPro workflow
#Based on API v1.0.0, Python 3.3
#Comments include notes for more advanced functionality

#See following forum discussions:
#http://www.agisoft.ru/forum/index.php?topic=2263.0
#http://www.agisoft.ru/forum/index.php?topic=1881.0

import os
import glob
import PhotoScan
import sys

#Need to set the following appropriately

#Path to photos
#photo_fn_path = "/tmp/export"
photo_fn_path = "/Volumes/SHEAN_PHOTO/photo/20140825_MammothTerraces_SfM/export_orig"
photo_fn_ext = "*.jpg"
#Path to ground control file, can contain orientation 
gc_fn = "/tmp/gcp.txt"
#Path to calibration file
cal_fn = "/tmp/D800_cal.xml"
#This is the base fn for output files
#out_fn = "/tmp/test"
out_fn = os.path.join(photo_fn_path, "test") 

#Define input coordinate system as WGS84
in_crs = PhotoScan.CoordinateSystem()
in_crs.init("EPSG::4326")
#Define output coordinate system as UTM 10N, WGS84
out_crs = PhotoScan.CoordinateSystem()
#out_crs.init("EPSG::32610")
#This is Yellowstone
out_crs.init("EPSG::32612")

#Add timestamp
print("Started")

#Create project file
doc = PhotoScan.app.document

#***
#NOTE: the following (loading photos, ground control, calibration, etc.) can be done manually
#***

#Load photos
new_chunk = PhotoScan.Chunk() 
new_chunk.label = "chunk1"

photo_fn_list = glob.glob(os.path.join(photo_fn_path, photo_fn_ext))
for photo_fn in photo_fn_list:
    new_chunk.cameras.add(photo_fn)

#Import ground control
gc = new_chunk.ground_control
gc.projection = in_crs
#Load EXIF data from photos
gc.loadExif()
#Alternatively, load csv containing file names and coordinates for photos
#gc.load(gc_fn, "csv")
#Set accuracy of camera positions in meters
#GeoXH
gc.accuracy_cameras = 0.5
#Nikon GP-1
#gc.accuracy_cameras = 5.0 
gc.apply()

#Import calibration 
#cal = PhotoScan.Calibration(cal_fn)
#new_chunk.calibration_mode('fixed')

#This adds the chunk to the project
doc.chunks.add(new_chunk)

#Update the GUI
PhotoScan.app.update()
doc.save(out_fn + "_init.psz")

#***
#NOTE: end of section with steps that can be accomplished manually
#***

#Grab the active chunk
chunk = doc.activeChunk

#Align photos
print("Aligning photos")
chunk.matchPhotos(accuracy="high", preselection="disabled")
#Use ground control if appropriate for input photos
#chunk.matchPhotos(accuracy="high", preselection="ground control")
chunk.alignPhotos()
PhotoScan.app.update()
doc.save(out_fn + "_sparse.psz")

#NOTE: markers should be manually identified here

#Build Dense Cloud
print("Building dense cloud")
chunk.buildDenseCloud(quality="medium", filter="mild")
PhotoScan.app.update()
doc.save(out_fn + "_dense.psz")

#Build Mesh
#NOTE: want to do this both with and without interpolation, export DEM for both
print("Building mesh")
chunk.buildModel(object="arbitrary", source="dense", interpolation="disabled", faces="high")
PhotoScan.app.update()
doc.save(out_fn + "_mesh_nointerp.psz")

#Want to test this smoothing - could help with TIN mesh artifacts
#chunk.smoothModel()

#Build Texture
#chunk.buildTexture(mapping="generic", blending="average", width=2048, height=2048)

#Export DEM
#Should automatically compute appropraite resolution/extent
print("Exporting DEM")
dem_fn = os.path.join(out_fn, "_dem.tif")
chunk.exportDem(dem_fn, format="tif", projeciton=out_crs)

#Export ortho
print("Exporting orthomosaic")
ortho_fn = os.path.join(out_fn, "_ortho.tif")
chunk.exportOrthophoto(ortho_fn, format="tif", blending="average", project=out_crs)

#Export point cloud
print("Exporting point cloud")
#Export las or xyz format
pc_type = "las"
#pc_type = "xyz"
pc_fn = os.path.join(out_fn, "_dense_wgs84.", pc_type)
#Export WGS84 point cloud
chunk.exportPoints(pc_fn, dense=True, precision=7, format=pc_type, projeciton=in_crs)
#Export projected point cloud
#For coord in meters, default precision of 6 is overkill
pc_fn = os.path.join(out_fn, "_dense_proj.", pc_type)
chunk.exportPoints(pc_fn, dense=True, precision=3, format=pc_type, projeciton=out_crs)

#Add timestamp
print("Finshed")


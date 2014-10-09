#! /bin/bash

#This will make a fast timelapse movie for nadir survey photos
#Want to make sure that orientation is consistent for all photos

jpg_list=$(ls *[0-9].jpg)

parallel -v -j 7 'convert -resize 640x640 {} {.}_sm.jpg' ::: $jpg_list

ffmpeg -r 10 -pattern_type glob -i '*_sm.jpg' -y -an movie.mp4 


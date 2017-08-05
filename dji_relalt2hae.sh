#! /bin/bash

exiftool *DNG | grep -i altitude

#DJI images contain the following tags:
#Absolute Altitude - elevation above msl
#Relative Altitude - altitude about home point
#GPS Altitude - altitude above home point
#GPS Altitude Ref - "Above Sea Level"

#Note that Relative Altitude and GPS altitude don't necessariliy agree
#Relative Altitude is likely barometer/sonic

#Need to compute elevation for each image above ellipsoid and replace the appropriate tags (read by Aigsoft/Pix4D)
#Use Absolute Altitude
#Or calculate home point absolute altitude (where relative altitude is 0), then add to all Relative Altitude tags
#Convert to HAE

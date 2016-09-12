#! /bin/bash

#David Shean
#dshean@gmail.com
#9/12/16

#Download logs from 3DR Solo filesystem via scp

#Connect to solo via wifi first

outdir=/tmp/logs

if [ ! -e $outdir ] ; then
    mkdir $outdir
fi
cd $outdir

#Interactive Connect
#ssh root@10.1.1.1

ip=10.1.1.1
user=root
pw=TjSDBkAu

#This contains all logs, including telemetry, exlcuding dataflash
dir=/log
#This dir appears empty
#dir=/log/solo/dataflash

scp -rp ${user}@${ip}:${dir}/* .


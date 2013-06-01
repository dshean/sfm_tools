#! /bin/tcsh -f

#Requires dcraw and ufraw

#set echo

echo

if ($#argv != 1) then
	echo "Usage is $0:t event_name"
	exit 1
endif 

#set carddir = '/Volumes/SHEAN_G10/DCIM/100CANON'
#set carddir = /Volumes/NIKON\ D800\ /DCIM/100ND800
set carddir = /Volumes/NIKON\ D800\ /DCIM/10*ND800
set photodir = /Volumes/ESS_STF_1TB/dshean

set jpgext = JPG
set rawext = NEF

set eventname = $1

set njpg = `ls $carddir/*$jpgext | wc -l`
set nraw = `ls $carddir/*$rawext | wc -l`

#What about turnover?  
#Might want to use time here to find first/last image
set firstimg = `ls $carddir/*.{$rawext,$jpgext} | head -1`
set lastimg = `ls $carddir/*.{$rawext,$jpgext} | tail -1`

#Should really check to make sure times are UTC here
#As of 6/26/12, using UTC times in camera

set firstimg_ts = `dcraw -i -v $firstimg | grep Timestamp | awk -F'Timestamp:' '{print $2}'`
set firstimg_ts = `date -j -f '%a %b %d %H:%M:%S %Y' "$firstimg_ts" +%Y%m%d`
set lastimg_ts = `dcraw -i -v $lastimg | grep Timestamp | awk -F'Timestamp:' '{print $2}'`
set lastimg_ts = `date -j -f '%a %b %d %H:%M:%S %Y' "$lastimg_ts" +%Y%m%d`

if ($firstimg_ts == $lastimg_ts) then
	set dir_ts = $firstimg_ts
else
	set dir_ts = ${firstimg_ts}_${lastimg_ts}
endif

set outdir = $photodir/${dir_ts}_${eventname}

#Check to see if another directory with the same eventname already exists
set olddir = (`ls $photodir | grep "_${eventname}/"`)

if ($#olddir == 1) then
    #Need to check that date range is inclusive
    echo "Using existing directory"
    set outdir = $olddir
endif

if (! -d $outdir) mkdir $outdir
if (! -d $outdir/$jpgext) mkdir $outdir/$jpgext
if (! -d $outdir/$rawext) mkdir $outdir/$rawext

set filelist = (`ls $carddir/*.{$rawext,$jpgext} | sort -u`)

set rawfilelist =  (`ls $carddir/*.$rawext`)
set jpgfilelist = (`ls $carddir/*.$jpgext`)

echo "Output directory: $outdir"
echo "$#filelist total files on card"
echo "$#rawfilelist $rawext files on card"
echo "$#jpgfilelist $jpgext files on card"

set n = 1

foreach i ($filelist)
#foreach i ($rawfilelist)
	echo "Processing $i"
	set img = $i:t:r
	set imgcount = `echo $img | awk -F'_' '{print $2}'`
	
	#Extract image creation date
	#set imgts = `identify -format "%[EXIF:DateTimeOriginal]" $i`
	set imgts = `dcraw -i -v $i | grep Timestamp | awk -F'Timestamp:' '{print $2}'`

    #Conver to UTC

	#Convert to desired output format
	#set outts = `date -j -f '%Y:%m:%d %H:%M:%S' $imgts +%Y%m%dT%H%M`
	set outts = `date -j -f '%a %b %d %H:%M:%S %Y' "$imgts" +%Y%m%d_%H%M`
	
	#Create subdirectory with datestamp
	#set subdir = `echo $outts | cut -c 1-8`
	#if (! -d $outdir/$subdir) then
	#	mkdir $outdir/$subdir
	#	mkdir $outdir/$subdir/$jpgext
	#	mkdir $outdir/$subdir/raw
	#endif

	#Extract camera info
	#set cam = `dcraw -i -v | grep Camera | awk -F'Camera:' '{print $2}'`
	#switch ($cam)
	#	case 'Canon EOS 40D':
	#		set camname = 40D
	#		breaksw
	#	case 'Canon PowerShot S3 IS':
	#		set camname = S3
	#		breaksw
	#	case 'NIKON E4800':
	#		set camname = E4800
	#		breaksw
	#	case 'OLYMPUS C300Z,D550Z':
	#		set camname = D550
	#		breaksw
	#	default:
	#		set camname = ""
	#		breaksw
	#endsw

    #set outname = `printf "%s_DES_%s_%04i" $outts $eventname $n`
	
    #Use the original shutter count instead of starting at 0
    set outname = `printf "%s_DES_%s_%s" $outts $eventname $imgcount`
    #set outname = `printf "%s_DES_%s_%04i" $outts $eventname $imgcount`

    set outext = $i:e

	cp -v -a $i $outdir/${outext:al}/$outname.${outext:al}
	#cp -v -a $i $outdir/raw/$outname.$rawext
	
	#Convert $rawext to $jpgext
	#Need to rotate
	#set dcraw_opt = (-v -w -H 0 -o 0 -q 3 -T)
	#dcraw $dcraw_opt $outdir/raw/$outname.$rawext
	#convert -quality 100 $outdir/raw/$outname.tiff $outdir/$jpgext/${outname}.$jpgext
	#exiftool -overwrite_original -TagsFromFile $outdir/raw/$outname.$rawext $outdir/$jpgext/$outname.$jpgext
	#rm $outdir/raw/$outname.tiff
	
	#if (!$status) then
		#rm $i
	#endif
	
	#cp -v -a ${i:r}.$jpgext $outdir/$jpgext/${outname}.$jpgext
	
	#if (!$status) then
		#rm ${i:r}.$jpgext
	#endif
	
	@ n++
	echo
	echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++"
	echo
end

set outrawfilelist =  (`ls $outdir/$rawext/*.$rawext`)
set outjpgfilelist = (`ls $outdir/$jpgext/*.$jpgext`)

if ($#rawfilelist != $#outrawfilelist) then
    echo
    echo "Warning: Number of output raw files does not match number of input raw files"
    echo "$#rawfilelist input files"
    echo "$#outrawfilelist output files"
endif

if ($#jpgfilelist != $#outjpgfilelist) then
    echo
    echo "Warning: Number of output $jpgext files does not match number of input $jpgext files"
    echo "$#jpgfilelist input files"
    echo "$#outjpgfilelist output files"
endif

exit

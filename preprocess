#!/bin/bash
#
#  This file preprocesses a directory holding an image/video dataset
#  It outputs into three directories:
#  
#  1. <img> resized images to defined WIDTH, FORMAT, base name, and EXTension
#  2. <vid> extracted frames resized to defined WIDTH, base name, and EXTension
#  3. <aud> extracted audio to defined format (AUDEXT)
#  
#  Finally, it outputs a .csv file holding original files and converted files
#  for later use, since filenames would otherwise be lost.
#
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
source paths
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
source ${SRC}/settings.sh # load settings < edit this file
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
function is_video()
{
	#	Check if file is video type
	ISVID=0
	for i in ${VIDFMT[@]}
	do
		if [[ "$1" == "$i" ]]
		then
			ISVID=1
			break
		fi 
	done
}

function grab_names()
{
	#	Place filenames in image or video arrays
	local dir=$1
	local fn=''
	for i in $dir/*
	do
		fn=$i
		is_video "${i: -3}"
		if [[ "$ISVID" == "1" ]]
		then
			VIDS[$VI]="$fn"
			((VI++))
		else
			IMGS[$II]="$fn"
			((II++))
		fi
	done
}

function convert_images()
{
	# Convert, resize, and rename filenames in image array
	# local digits="0${#II}"
	local fn=''
	local cnt=0
	for i in ${IMGS[@]}
	do
		fn=`printf "%s/%s-%d%s" "$IMG" "$IMGBASE" "$cnt" ".${EXT}"`
		# fn=`printf "%s/%s-%${digits}d%s" "$IMG" "$IMGBASE" "$cnt" ".${EXT}"`
		sips -s format "$FORMAT" --resampleWidth "$WIDTH" "$i" --out "$fn"
		printf "%s,%s\n" "$i" "$fn" >> $LOG/conversion.csv
		((cnt++))
	done
}

function convert_videos()
{
	# Extract images, resize, and rename filenames in video array
	# Extract audio as well
	# local frames=''
	# local digits=''
	local fn=''
	local cnt=0
	for i in ${VIDS[@]}
	do
		fn=${VIDBASE}-${cnt}
		# frames=`ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of default=nokey=1:noprint_wrappers=1 $i`
		# digits="0${#frames}"
		ffmpeg -i "$i" -f "${IMGFMT}" -vf "scale=$WIDTH:-1" -start_number 0 "${VID}/${fn}-%d.${EXT}" -f "${AUDEXT}" -vn "${AUD}/${fn}.${AUDEXT}"
		# ffmpeg -i "$i" -f "${IMGFMT}" -vf "scale=$WIDTH:-1" "${VID}/${fn}-%${digits}d.${EXT}" -f "${AUDEXT}" -vn "${AUD}/${fn}.${AUDEXT}"
		printf "%s,%s\n" "$i" "${VID}/${fn}-*.${EXT}" >> $LOG/conversion.csv
		printf "%s,%s\n" "$i" "${AUD}/${fn}.${AUDEXT}" >> $LOG/conversion.csv
		((cnt++))
	done

}

GRABDIR=$RAW

if [[ $1 ]] && [[ -d $1 ]]
then
	echo "Getting names from $1"
	GRABDIR=$1
else
	echo "Getting names from raw directory (default)"
fi

read -p "Do you wish to continue? y/n (y)" -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]
then
	exit
fi


echo "original,converted" > $LOG/conversion.csv


if [[ $II ]]
then
	echo "Converting $II image(s)..."
	convert_images
else
	echo "No images found."
fi

if [[ $VI ]]
then
	echo "Converting $MI video(s)..."
	convert_videos
else
	echo "No videos found."
fi





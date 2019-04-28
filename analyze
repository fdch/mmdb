#!/bin/bash

# LATER: make sure you don't run out of memory!

source ./src/paths.sh
source ./src/settings.sh

PDPATCH="analyze.pd"


PARAMS=(
# blob area threshold
# luminance threshold
";blobs-params 80 91"

# maximum nuber of circles detected ( default : 10 )
# threshold ( default 100 )
# threshold2 ( default 10 )
# minimum distance between circles ( default : 30 )
# detector resolution ( default 1 )
";circles-params 20 11 4 15 10"

# maximum nuber of lines detected ( default : 10 )
# CV_HOUGH_STANDARD | CV_HOUGH_PROBABILISTIC | CV_HOUGN_MULTI_SCALE
# threshold ( default 50 )
# minimum length ( default 30, for mode CV_HOUGH_PROBABILISTIC )
# gap betwwen lines ( default 10, for mode CV_HOUGH_PROBABILISTIC )
# angle resolution ( default 1, for mode CV_HOUGH_MULTI_SCALE )
# distance resolution ( default 1, for mode CV_HOUGH_MULTI_SCALE )
";lines-params 20 1 66 35 10 10 12"

# quantile
";histo-params 0.67"

# minimum distance
# quality
";keypoints-params 10 100"

# xml file for face recognition
";faces-params load ${PWD}/haarcascade/haarcascade_frontalface_alt.xml"

# xml file for full body recognition
";bodies-params load ${PWD}/haarcascade/haarcascade_fullbody.xml" 

# roi text
";roi-txt symbol ${TXT}/roi.txt"

# clustering parameters 
# 1. reduction percentage of the original image x/100
# 2. N clusters
";cluster-params 5 5"

#LATER: do same roi thing with thresholds for blob-params

)


function analyze()
{
	# `analyze` takes three arguments
	# 1. files: like multiimage `open` message: path/to/file/base-*.extension
	# 2. target: prefix to name analysis files
	# 3. roi-flag 1/0 to set roi defined in roi text
	
	local files=$1
	local base=`dirname "$files"`
	local target=$2
	local roi=$3
	local cnt=0
	local msg=''
	if [[ ! $4 ]]
	then
		for img in ${base}/*.${EXT}
		do
			((cnt++))
		done
		((cnt--))
	else
		cnt=$4
	fi
	msg="${PARAMS[@]}"
	msg+=";roi-flag ${roi}" # roi flag
	msg+=";analyze list ${files} ${cnt} ${target}"

	# echo "${msg}"
	cd $BIN
	$PD -batch -send "${msg}" -open "${PDPATCH}"
}

analyze "${VID}/${VIDBASE}-0-*.${EXT}" "videos" 1 $1
analyze "${IMG}/${IMGBASE}-*.${EXT}" "images" 0 $1



#!/bin/bash

IMGBASE=i   	# base name for image files
VIDBASE=v   	# base name for video files
FORMAT=jpeg 	# `sips` format for image files
IMGFMT=image2   # `ffmpeg` image format for frame extraction
EXT=jpg 		# image extension format
AUDEXT=wav 		# audio extension format
WIDTH=320   	# width for image and video files
CNT=0       	# count for name indices
VI=0        	# index for video files
VIDS=()     	# array to store video file names
II=0        	# index for image files
IMGS=()     	# array to store image file names
ISVID=0     	# flag to check if file is video

# array storing some video file extensions
VIDFMT=( "MOV" "mov" "MP4" "mp4" "AVI" "avi" "MKV" "mkv" )
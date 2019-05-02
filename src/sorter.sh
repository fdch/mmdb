#!/bin/bash

source paths
source ./src/paths.sh
source ../src/paths.sh

function sort_it()
{
	local f=''
	local ln=''
	local tmp=/tmp/sorted
	for i in "${@}"
	do
		f+="-k${i} "
	done
	sort ${f} "${TEXT}.txt" | cut -f 1 -d ' ' > "${tmp}"
	while read line
	do
		ln+="$line "
	done < "${tmp}"
	echo "${ln}" >> "${SORTED}"
}

for BASE in images videos
do
	TEXT=${TXT}/${BASE}-entries
	SORTED=${TXT}/${BASE}-sorted.txt

	printf "%s" > "${SORTED}"

	# Sort by each field starting from 2nd field
	for i in {2..8}
	do
		sort_it $i
	done

	# Sort by pairs of fields
	sort_it 3 4 	# bodies and faces
	sort_it 5 8 	# blobs and keypoints
	sort_it 6 7 	# lines and circles
	sort_it {5..8} 	# lines,circles,blobs, and keypoints
	sort_it {2..8} 	# use all fields

done

#!/bin/bash

source paths
source ./src/paths.sh
source ../src/paths.sh

if [[ -d $1 ]]
then
	NAME=`basename $1`
	SOURCE_DIR="${PWD}/${NAME}"
	TEXTFILE="${TXT}/${NAME}_path_file.txt"
else
	echo "analyze_sounds.sh: Source directory not provided. Exiting."
	exit 1
fi

if [[ -d $2 ]]
then
	TARGET_DIR="${PWD}/`basename $2`"
else
	# Where to put all the *.timid files
	echo "analyze_sounds.sh: Target directory not provided. Exiting."
	exit 1
fi	

function get_text()
{

	local path=$1
	local textfile=$2
	local c=0

	printf "" > ${textfile}
	for i in ${path}/*
	do
		if [[ $3 ]]
		then
			if [[ $3 == $c ]]
			then
				printf "%s %s\n" $i `basename $i .wav` >> ${textfile}
				return
			fi
		else
			printf "%s %s\n" $i `basename $i .wav` >> ${textfile}
		fi
		((c++))
	done
}


function analyze_sounds()
{
	local pdpatch="analyze_sounds.pd"
	local msg=''
	local pdmsg=(
		";automator 1;"  # Enables/Disables automator for batch processing
		";data_dir ${TARGET_DIR};"  # Where to put all the *.timid files
		";load_sounds ${TEXTFILE};" # File containing <path> <filename>
		";" # placeholder for variable argument
		)

	# if requesting only one, then only load an analyze that one
	if [[ $1 ]]
	then
		get_text "${SOURCE_DIR}" "${TEXTFILE}" "$1"
		pdmsg[0]=";automator 0;"
		pdmsg[3]=";analyze_one $1;"
	else
		get_text "${SOURCE_DIR}" "${TEXTFILE}"
	fi
	
	msg="${pdmsg[@]}" # make pd message into a nice string we can pass
	
	cd $BIN
	$PD -batch -send "${msg}" -open "${pdpatch}"

}

analyze_sounds $3


MAKE_AUDIO_DB="${SRC}/make_audio_db.py"
TIMID_FILES_DIR="${TARGET_DIR}"
AUDIO_DATA_FILE="${DATA}/audio-data.json"


/usr/bin/python "${MAKE_AUDIO_DB}" "${TIMID_FILES_DIR}" "${AUDIO_DATA_FILE}"


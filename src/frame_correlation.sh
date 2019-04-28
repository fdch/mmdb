#!/bin/bash
ROOTDIR=~/Documents/fd_work
PATCHDIR=$ROOTDIR/visual_music/diana
WHICHPD=Pd-0.49-1-i386
PD=/Applications/$WHICHPD.app/Contents/Resources/bin/pd
BINDIR=$PATCHDIR/bin

function frame_corr()
{
	local pdfile=frame_correlation
	local pdmess=""
	local t
	local n
	local fn
	local fp
	if [ "$#" -ne 4 ]
	then
		echo 
"
	Usage: 
		${pdfile} threshold number_of_files filename path
		EXAMPLE:
			${pdfile} 0.7 300 subway ~/Documents/subway-img
"
		return
	else
		t=$1
		n=$2
		fn=$3
		fp=$4
		pdmess="$;threshold ${t};${pdfile} ${n} ${fn} ${fp};pd quit"
	fi

	cd $BINDIR
	# echo -batch -send "\"$pdmess\"" -open "${pdfile}.pd"
	# $PD -send "$pdmess" -open "${pdfile}.pd"
	$PD -batch -stderr -send "$pdmess" -open "${pdfile}.pd"
	cat "$PATCHDIR/txt/${pdfile}-${fn}-${n}.txt"
}


function hist_corr()
{
	local pdfile=histogram_correlation
	local pdmess=""
	local n
	local fn
	local fp
	if [ "$#" -ne 3 ]
	then
		echo 
"
	Usage: 
		${pdfile} number_of_files filename path
		EXAMPLE:
			${pdfile} 300 subway ~/Documents/subway-img
"
		return
	else
		n=$1
		fn=$2
		fp=$3
		pdmess=";${pdfile} ${n} ${fn} ${fp}; pd quit"
	fi

	cd $BINDIR
	# echo -batch -send "\"$pdmess\"" -open "${pdfile}.pd"
	# $PD -send "$pdmess" -open "${pdfile}.pd"
	$PD -batch -stderr -send "$pdmess" -open "${pdfile}.pd"
	cat "$PATCHDIR/txt/${pdfile}-${fn}-${n}.txt"
}

FILENUM=10
FILENAME=subway
FILEPATH=~/Documents/subway-img

ARGS=( "$FILENUM" "$FILENAME" "$FILEPATH" )


histogram_correlation=`hist_corr ${ARGS[@]}`
frame_correlation=`frame_corr 0.7 ${ARGS[@]}`

# echo $histogram_correlation
# echo $frame_correlation
echo "
${ARGS[@]}
----------------------------------------------
"
echo $histogram_correlation histogram correlation | column -t
echo $frame_correlation frame_correlation | column -t



exit
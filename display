#!/bin/bash

source paths
source ./src/paths.sh
source ../src/paths.sh

PDFILE=netread.pd

MSG=";pix_multiimage open ${IMG}/i-*.jpg 590"
MSG+=";gemwin create,1"

cd ${BIN}

$PD -nogui -send "${MSG}" -open "${PDFILE}" & echo $!
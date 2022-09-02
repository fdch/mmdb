#!/bin/bash

source paths



PDFILE=netread.pd

MSG=";pix_multiimage open ${IMG}/i-*.jpg 590"
MSG+=";gemwin create,1"

cd ${BIN}

$PD -nogui -send "${MSG}" -open "${PDFILE}" & echo $!
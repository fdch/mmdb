#!/bin/bash

source ./src/paths.sh

PDFILE=netread.pd

MSG=";pix_multiimage open ${IMG}/i-*.jpg 590"
MSG+=";gemwin create,1"

$PD -nogui -send "${MSG}" -open "${BIN}"/"${PDFILE}" 
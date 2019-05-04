#!/bin/bash

source paths


PDFILE=analyze_sounds.pd

cd ${BIN}

$PD -open "${BIN}/${PDFILE}" & echo $!
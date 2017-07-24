#!/bin/bash

expr=${PWD}
testid=$(basename $expr)

# mosaic
cd post_pro_val_result
gdal_merge.py -init 0 -a_nodata 0 -o ${testid}_out.tif *.tif


for tif in $(ls *_blob_0.tif) ; do

	gdal_calc.py -A ${testid}_out.tif -B ${tif}  --outfile=${testid}_out.tif --calc="maximum(A,B)"  --debug --type='Byte' --overwrite

	exit
done

#!/bin/bash

rm  post_pro_val_result/*
mkdir post_pro_val_result

eo_dir=/home/hlc/codes/DeepNetsForEO/notebooks
expr=${PWD}
testid=$(basename $expr)

# copy result
# crop result file based on original image (and save to tif format) 
# georeference
while read line_id <&3 && read line_file <&4
do
	echo $line_id $line_file
	cp features/deeplab_largeFOV/val/fc8/${line_id}_blob_0.png post_pro_val_result/.
	cd post_pro_val_result
	size=$(gdalinfo ${line_file} | grep "Size is" ) 
	width=$(echo $size | cut -d' ' -f 3 )
	width=${width::-1}
	#echo "width:" $width
	height=$(echo $size | cut -d' ' -f 4 )
	#echo $height
	#echo $width $height ${line_id}_blob_0.png ${line_id}_blob_0.tif
	
	gdal_translate -srcwin 0 0 $width $height ${line_id}_blob_0.png ${line_id}_blob_0.tif 			
	../gdalcopyproj.py $line_file ${line_id}_blob_0.tif 
	cd ..

done 3< "list/val_id.txt" 4< "list/val.txt"

# mosaic
cd post_pro_val_result
#gdal_merge.py -init 0 -a_nodata 0 -o ${testid}_out.tif *.tif
${eo_dir}/mosaic_patches.py -s ../split_image_info.txt  -o ${testid}_out.tif *.tif
rm *p_c_*.tif
rm out_*

# convert to shapefile
gdal_polygonize.py -8 ${testid}_out.tif -b 1 -f "ESRI Shapefile" ${testid}_gully.shp

cd ..

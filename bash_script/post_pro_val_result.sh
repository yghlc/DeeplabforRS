#!/bin/bash

para_file=para.ini
para_py=/home/hlc/codes/PycharmProjects/DeeplabforRS/parameters.py

SECONDS=0

rm  post_pro_val_result/*
mkdir post_pro_val_result

eo_dir=$(python2 ${para_py} -p ${para_file} codes_dir)
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
	${eo_dir}/gdalcopyproj.py $line_file ${line_id}_blob_0.tif
	cd ..

done 3< "list/val_id.txt" 4< "list/val.txt"

# mosaic
cd post_pro_val_result
#gdal_merge.py -init 0 -a_nodata 0 -o ${testid}_out.tif *.tif
${eo_dir}/mosaic_patches.py -s ../split_image_info.txt  -o ${testid}_out.tif *.tif
#rm *p_c_*.tif
#rm out_*

# set 0 as no data
gdal_translate -a_nodata 0 ${testid}_out.tif ${testid}_out_nodata.tif
mv ${testid}_out_nodata.tif ${testid}_out.tif

# convert to shapefile
gdal_polygonize.py -8 ${testid}_out.tif -b 1 -f "ESRI Shapefile" ${testid}.shp

# post processing of shapefile
cp ../${para_file}  ${para_file}
min_area=$(python2 ${para_py} -p ${para_file} minimum_gully_area)
min_p_a_r=$(python2 ${para_py} -p ${para_file} minimum_ratio_perimeter_area)
${eo_dir}/polygon_post_process.py -p ${para_file} -a ${min_area} -r ${min_p_a_r} ${testid}.shp ${testid}_post.shp

cd ..

duration=$SECONDS
echo "$(date): time cost of the post processing: ${duration} seconds">>"time_cost.txt"
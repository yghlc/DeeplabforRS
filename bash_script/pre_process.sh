#!/bin/bash

root=/home/hlc/Data/eboling/eboling_uav_images/dom
train_shp=/home/hlc/Data/eboling/training_validation_data/gps_rtk/gps_rtk_polygons_3_fix.shp
eo_dir=/home/hlc/codes/PycharmProjects/DeeplabforRS

# current folder (without path)
test_dir=${PWD##*/}


rm ${root}/${test_dir}/top/*
rm ${root}/${test_dir}/gts_numpy/*
rm ${root}/${test_dir}/split_images/*
rm ${root}/${test_dir}/split_labels/*

mkdir ${root}/${test_dir}/top ${root}/${test_dir}/gts_numpy ${root}/${test_dir}/split_images ${root}/${test_dir}/split_labels

###pre-process UAV images
${eo_dir}/extract_target_imgs.py -n 255 -b 100 --rectangle $train_shp  ${root}/UAV_DOM_Eboling_0.48m.tif  -o ${root}/${test_dir}/top
${eo_dir}/extract_target_imgs.py -n 255 -b 100 --rectangle $train_shp ${root}/raster_class_version_gps_rtk_3_fix_add.tif  -o ${root}/${test_dir}/gts_numpy

for img in $(ls ${root}/${test_dir}/top/*.tif)
do
${eo_dir}/split_image.py -W 321 -H 321 -o  ${root}/${test_dir}/split_images $img
done

for label in $(ls ${root}/${test_dir}/gts_numpy/*.tif)
do
${eo_dir}/split_image.py -W 321 -H 321 -o ${root}/${test_dir}/split_labels $label
done


#prepare list files
find ${root}/${test_dir}/split_images/*.tif > list/image_list.txt
find ${root}/${test_dir}/split_labels/*.tif > list/label_list.txt

paste list/image_list.txt list/label_list.txt | awk ' { print $1 " " $2 }' > list/temp.txt
cp list/temp.txt list/train_aug.txt
cp list/image_list.txt list/val.txt
list/extract_fileid.sh list/val

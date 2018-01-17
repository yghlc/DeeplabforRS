#!/bin/bash

para_file=para.ini
para_py=/home/hlc/codes/PycharmProjects/DeeplabforRS/parameters.py

root=$(python2 ${para_py} -p ${para_file} working_root)
train_shp=$(python2 ${para_py} -p ${para_file} training_polygons)
eo_dir=$(python2 ${para_py} -p ${para_file} codes_dir)


SECONDS=0

input_image=$(python2 ${para_py} -p ${para_file} input_image_path)
# input groud truth (raster data with pixel value)
input_GT=$(python2 ${para_py} -p ${para_file} input_ground_truth_image)

# current folder (without path)
test_dir=${PWD##*/}

# remove the previous extracted images
rm ${root}/${test_dir}/top/*
rm ${root}/${test_dir}/gts_numpy/*

mkdir ${root}/${test_dir}/top ${root}/${test_dir}/gts_numpy ${root}/${test_dir}/split_images ${root}/${test_dir}/split_labels

###pre-process UAV images, extract the training data from the whole image
dstnodata=$(python2 ${para_py} -p ${para_file} dst_nodata)
buffersize=$(python2 ${para_py} -p ${para_file} buffer_size)
rectangle_ext=$(python2 ${para_py} -p ${para_file} b_use_rectangle)

${eo_dir}/extract_target_imgs.py -n ${dstnodata} -b ${buffersize} ${rectangle_ext} $train_shp ${input_image}  -o ${root}/${test_dir}/top
${eo_dir}/extract_target_imgs.py -n ${dstnodata} -b ${buffersize} ${rectangle_ext} $train_shp ${input_GT}  -o ${root}/${test_dir}/gts_numpy

# remove the previous split images
rm ${root}/${test_dir}/split_images/*
rm ${root}/${test_dir}/split_labels/*

### split the training image to many small patch
patch_w=$(python2 ${para_py} -p ${para_file} train_patch_width)
patch_h=$(python2 ${para_py} -p ${para_file} train_patch_height)
overlay=$(python2 ${para_py} -p ${para_file} train_pixel_overlay)     # the overlay of patch in pixel

for img in $(ls ${root}/${test_dir}/top/*.tif)
do
${eo_dir}/split_image.py -W ${patch_w} -H ${patch_h}  -e ${overlay} -o  ${root}/${test_dir}/split_images $img
done

for label in $(ls ${root}/${test_dir}/gts_numpy/*.tif)
do
${eo_dir}/split_image.py -W ${patch_w} -H ${patch_h}  -e ${overlay} -o ${root}/${test_dir}/split_labels $label
done


#prepare list files
find ${root}/${test_dir}/split_images/*.tif > list/image_list.txt
find ${root}/${test_dir}/split_labels/*.tif > list/label_list.txt

paste list/image_list.txt list/label_list.txt | awk ' { print $1 " " $2 }' > list/temp.txt
cp list/temp.txt list/train_aug.txt
cp list/image_list.txt list/val.txt
list/extract_fileid.sh list/val

duration=$SECONDS
echo "$(date): time cost of preparing training images: ${duration} seconds">>"time_cost.txt"
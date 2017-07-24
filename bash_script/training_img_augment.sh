#!/bin/bash

root=/home/hlc/Data/eboling/eboling_uav_images/dom
eo_dir=/home/hlc/codes/PycharmProjects/DeeplabforRS
augscript=${eo_dir}/image_augment.py
test_dir=EbolingUAV_deeplab_7

# only augmentation on gully images
mkdir split_images_temp
mkdir split_labels_temp 
for id in $(seq 12 23); do
	echo $id
	mv split_images/UAV_DOM_Eboling_0.48m_${id}_*.tif split_images_temp/.
	mv split_labels/raster_class_version_gps_rtk_3_fix_add_${id}_*.tif  split_labels_temp/.
done

#update list
./get_list.sh

#exit 
#backup 
cp list/image_list.txt list/image_list_without_augmentation.txt
cp list/label_list.txt list/label_list_without_augmentation.txt

#augment training images
${augscript} list/image_list.txt -o ${root}/${test_dir}/split_images

#augment training lables
${augscript} list/label_list.txt -o ${root}/${test_dir}/split_labels
# force the groud truth only have 0 and 1 after augmentation; could loss some pixel
for item in $(ls ${root}/${test_dir}/split_labels/*.tif)
do
    gdal_calc.py -A $item  --outfile=${item} --calc="A==1"  --debug --type='Byte' --overwrite
done

# mv file back
mv split_images_temp/* split_images/.
mv split_labels_temp/* split_labels/.

# update list file
./get_list.sh


#!/bin/bash

para_file=para.ini
para_py=/home/hlc/codes/PycharmProjects/DeeplabforRS/parameters.py

if [ "$#" -ne 1 ]; then
    echo "please input the id of gpu"
    exit
fi



eo_dir=$(python2 ${para_py} -p ${para_file} codes_dir)

#/home/hlc/Data/eboling/eboling_uav_images/dom/EbolingUAV_deeplab_7
expr=${PWD}
gpuid=$1

SECONDS=0

patch_w=$(python2 ${para_py} -p ${para_file} inf_patch_width)     # the expected width of patch
patch_h=$(python2 ${para_py} -p ${para_file} inf_patch_height)     # the expected height of patch
overlay=$(python2 ${para_py} -p ${para_file} inf_pixel_overlay)     # the overlay of patch in pixel

# inference the same image of input images for training
RSimg=$(python2 ${para_py} -p ${para_file} input_image_path)

cp ~/codes/rsBuildingSeg/DeepLab-Context/run_train.py .
cp ~/codes/rsBuildingSeg/DeepLab-Context/run_test_and_evaluate.py .

rm -r features
rm -r inf_split_images
mkdir -p inf_split_images

###pre-process UAV images
${eo_dir}/split_image.py -W ${patch_w} -H ${patch_h} -e ${overlay} -o ${PWD}/inf_split_images ${RSimg}

# get file list
#find ${PWD}/inf_split_images/*.tif > list/inf_images.txt
rm list/inf_images.txt; for img in ${PWD}/inf_split_images/*.tif; do echo $img >> list/inf_images.txt ; done

cd list
cp inf_images.txt val.txt
./extract_fileid.sh val
cd ..

duration=$SECONDS
echo "$(date): time cost of preparing inference images: ${duration} seconds">>"time_cost.txt"

SECONDS=0

python ./run_test_and_evaluate.py ${expr} ${gpuid}

duration=$SECONDS
echo "$(date): time cost of inference: ${duration} seconds">>"time_cost.txt"



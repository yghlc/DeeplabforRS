#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "please input the id of gpu"
    exit
fi

eo_dir=/home/hlc/codes/PycharmProjects/DeeplabforRS

#/home/hlc/Data/eboling/eboling_uav_images/dom/EbolingUAV_deeplab_7
expr=${PWD}
gpuid=$1



patch_w=321     # the expected width of patch
patch_h=321     # the expected height of patch
overlay=150     # the overlay of patch in pixel

RSimg=../UAV_DOM_Eboling_0.48m.tif

cp ~/codes/rsBuildingSeg/DeepLab-Context/run_train.py .
cp ~/codes/rsBuildingSeg/DeepLab-Context/run_test_and_evaluate.py .

rm -r features
rm -r inf_split_images
mkdir inf_split_images

###pre-process UAV images
${eo_dir}/split_image.py -W ${patch_w} -H ${patch_h} -e ${overlay} -o ${PWD}/inf_split_images ${RSimg}

find ${PWD}/inf_split_images/*.tif > list/inf_images.txt
cd list
cp inf_images.txt val.txt
./extract_fileid.sh val
cd ..

python ./run_test_and_evaluate.py ${expr} ${gpuid} 


# post processing 
./post_pro_val_result.sh

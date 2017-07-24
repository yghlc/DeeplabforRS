#!/bin/bash

cd ~/codes/rsBuildingSeg
git pull
cd -

expr=/home/hlc/Data/eboling/eboling_uav_images/dom/EbolingUAV_deeplab_7
gpuid=0

cp ~/codes/rsBuildingSeg/DeepLab-Context/run_train.py .
cp ~/codes/rsBuildingSeg/DeepLab-Context/run_test_and_evaluate.py .

rm -r features
mkdir inf_split_images

###pre-process UAV images
/home/hlc/codes/DeepNetsForEO/notebooks/split_image.py -W 321 -H 321 -e 150 -o ${PWD}/inf_split_images ../UAV_DOM_Eboling_0.48m.tif

find ${PWD}/inf_split_images/*.tif > list/inf_images.txt
cd list
cp inf_images.txt val.txt
./extract_fileid.sh val
cd ..

python ./run_test_and_evaluate.py ${expr} ${gpuid} 


# post processing 
./post_pro_val_result.sh

#!/usr/bin/env bash


cd ~/codes/rsBuildingSeg
git pull
cd -

eo_dir=/home/hlc/codes/PycharmProjects/DeeplabforRS
cd ${eo_dir}
git pull
cd -

expr=${PWD}
gpuid=1

cp ~/codes/rsBuildingSeg/DeepLab-Context/run_train.py .
cp ~/codes/rsBuildingSeg/DeepLab-Context/run_test_and_evaluate.py .

${eo_dir}/bash_script/pre_process.sh

python ./run_train.py ${expr} ${gpuid}

#Resuming
#/home/lchuang/codes/rsBuildingSeg/DeepLab-Context/.build_release/tools/caffe.bin train --solver=/home/lchuang/experiment/caffe_deeplab/spacenet_rgb_aoi_2-4/config/deeplab_largeFOV/solver_train_aug.prototxt --snapshot=/home/lchuang/experiment/caffe_deeplab/spacenet_rgb_aoi_2-4/model/deeplab_largeFOV/train_iter_28000.solverstate  --gpu=6

#/home/hlc/codes/rsBuildingSeg/DeepLab-Context/.build_release/tools/caffe.bin train --solver=/home/hlc/Data/eboling/eboling_uav_images/dom/EbolingUAV_deeplab_3/config/deeplab_largeFOV/solver_train_aug.prototxt --snapshot=/home/hlc/Data/eboling/eboling_uav_images/dom/EbolingUAV_deeplab_3/model/deeplab_largeFOV/train_iter_2000.solverstate  --gpu=1

${eo_dir}/bash_script/inference.sh ${gpuid}

${eo_dir}/bash_script/post_pro_val_result.sh
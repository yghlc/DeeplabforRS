#!/usr/bin/env bash

# randomly selected 80% images for training

#N=5
## test
#cd ~/Data/eboling/eboling_uav_images
#
#ls |sort -R |tail -$N |while read file;
#do
#    echo $file
#    # Something involving $file, or you can leave
#    # off the while to just get the filenames
#done
#


# randomly selected 70% ground truth polygons (70% for non-gully and gully,separately)
# for ten time
eo_dir=~/codes/PycharmProjects/DeeplabforRS
cd ${eo_dir}
git pull
cd -

gt_shp=~/Data/eboling/training_validation_data/manually_identify/train_polygons_digitize_gps_v6.shp
#out_dir=~/Data/eboling/training_validation_data/manually_identify/randomly_select_training_polygons

#
out_dir=~/Data/eboling/training_validation_data/manually_identify/randomly_select_training_polygons_gully_only

mkdir ${out_dir}

for ii in {1..10}
do
    echo "get ${ii} random training polygons"
    ${eo_dir}/get_trianing_polygons.py ${gt_shp} ${out_dir}/train_polygon_random_${ii}.shp

done



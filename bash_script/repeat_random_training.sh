#!/usr/bin/env bash


# change the training polygons, then repeat training
# e.g., working folder on Cryo03: ~/Data/eboling/eboling_uav_images/dom/EboDOM_deeplab_31

time_str=`date +%Y_%m_%d_%H_%M_%S`
echo ${time_str}

# backup previous results

mv result_backup result_backup_${time_str}
mkdir files_backup_${time_str}
mv raster_class_train_polygon*.tif files_backup_${time_str}/.
mv processLog.txt files_backup_${time_str}/.
mv time_cost.txt files_backup_${time_str}/.

# new tests
mkdir result_backup

for ii in {1..5};
do

# change para.ini and pre_para.ini
cp pre_para.ini.template pre_para.ini
sed -i -e  s/random_x/random_${ii}/g pre_para.ini
cp para.ini.template para.ini
sed -i -e  s/random_x/random_${ii}/g para.ini

#exit

# run
./exe.sh

# copy result
./backup_results.sh random_${ii}

done



#!/bin/bash

for expr in $(ls -d ${PWD}/../EbolingUAV_deeplab* ); do
	folder=$(basename $expr)
	echo $folder 

	mkdir $folder
	cd $folder
	cp -r ${expr}/config .
	cp -r ${expr}/log .
	cp -r ${expr}/list .
	cp ${expr}/*.sh .
	cp ${expr}/*.py .
	mkdir -p model/deeplab_largeFOV
	newest_model=$(ls -t ${expr}/model/deeplab_largeFOV/*00.caffemodel | head -1)
	cp -r $newest_model model/deeplab_largeFOV/.
	cp -r ${expr}/post_pro_val_result* .
	for result in $(ls -d  post_pro_val_result post_pro_val_result_*); do 
	    cd $result
	    rm *_blob_0.*
	    cd ..
	done	

	cd ..

done


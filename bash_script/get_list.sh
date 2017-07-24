#!/bin/bash

#prepare list files
find ${PWD}/split_images/*.tif > list/image_list.txt
find ${PWD}/split_labels/*.tif > list/label_list.txt

paste list/image_list.txt list/label_list.txt | awk ' { print $1 " " $2 }' > list/temp.txt
cp list/temp.txt list/train_aug.txt
cp list/image_list.txt list/val.txt
list/extract_fileid.sh list/val

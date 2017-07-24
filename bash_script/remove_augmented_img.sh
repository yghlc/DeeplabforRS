#!/bin/bash
cp list/image_list_without_augmentation.txt list/image_list.txt
cp list/label_list_without_augmentation.txt list/label_list.txt

paste list/image_list.txt list/label_list.txt | awk ' { print $1 " " $2 }' > list/temp.txt
cp list/temp.txt list/train_aug.txt
cp list/image_list.txt list/val.txt
list/extract_fileid.sh list/val


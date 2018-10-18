#!/usr/bin/env bash

# randomly selected 80% images for training

N=5

# test
cd ~/Data/eboling/eboling_uav_images

ls |sort -R |tail -$N |while read file;
do
    echo $file
    # Something involving $file, or you can leave
    # off the while to just get the filenames
done


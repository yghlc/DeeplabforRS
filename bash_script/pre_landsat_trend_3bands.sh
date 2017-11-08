#!/usr/bin/env bash

#input landsat trend
trend_folder=/home/hlc/Data/Qinghai-Tibet/LinLiuTibet_Trends/Beiluhe
fname=Tibet_Beiluhe_004_ndvi_mos
input=${trend_folder}/${fname}.tif

#convert trend with [-1,1] to [0,255]
gdal_contrast_stretch -percentile-range 0.02 0.98 ${input}  ${fname}_8bit.tif

#extract first three bands for deeplab (most of them have three bands, one of them only have one band)
# use ndvi
gdal_translate -b 1 -b 2 -b 3 ${fname}_8bit.tif ${fname}_8bit_3bands.tif


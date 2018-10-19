#!/usr/bin/env bash

# get the boundary of valid pixel on the DOM, that is, without the no-data pixels.

DOM=~/Data/eboling/eboling_uav_images/dom/UAV_DOM_Eboling.tif
DOM_tmp=~/Data/eboling/eboling_uav_images/dom/UAV_DOM_Eboling_tmp.tif
#DOM_tmp2=~/Data/eboling/eboling_uav_images/dom/UAV_DOM_Eboling_tmp2.tif

mkdir ~/Data/eboling/eboling_uav_images/dom/dom_extent
out_shp=~/Data/eboling/eboling_uav_images/dom/dom_extent/dom_extent.shp

## add no-data
#gdalwarp -dstnodata 0 -of GTiff ${DOM} ${DOM_tmp}
#
## add band 4 as mask band
#gdalwarp -dstalpha -of GTiff ${DOM_tmp} ${DOM_tmp2}

# the nodata value is zero
gdal_calc.py -A ${DOM} --A_band=1 --outfile=${DOM_tmp} --calc="255*(A>0)" --NoDataValue=0

# get the boundary based on band 4
# the result turns out have three polygons (two more tiny polygons, so I delete them manually)
gdal_polygonize.py ${DOM_tmp} -b 1 -f "ESRI Shapefile" ${out_shp}

#
rm ${DOM_tmp}
#!/usr/bin/env bash

#input original dem file
orig_dem=~/Data/eboling/DEM/20160728-Large-DSM-NaN.tif
dem_8bit=~/Data/eboling/DEM/20160728-Large-DSM-NaN_8bit.tif
dem_8bit_res=~/Data/eboling/DEM/20160728-Large-DSM-NaN_8bit_0.15.tif

#dem_8bit_3b=~/Data/eboling/DEM/20160728-Large-DSM-NaN_8bit_3bands.tif


#convert orginal DEM from [min,max] to [0,255]
gdal_contrast_stretch -percentile-range 0.02 0.98 ${orig_dem}  ${dem_8bit}


# resample to 0.15, 0.15, the same as the DOM
rm ${dem_8bit_res}
gdalwarp -tr 0.15 0.15 -r "cubic" ${dem_8bit} ${dem_8bit_res}





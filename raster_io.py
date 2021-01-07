#!/usr/bin/env python
# Filename: raster_io 
"""
introduction:  Based on rasterio, to read and write raster data

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 03 January, 2021
"""

import os, sys
from optparse import OptionParser
import rasterio
import numpy as np

def open_raster_read(raster_path):
    src = rasterio.open(raster_path)
    return src

def get_width_heigth_bandnum(opened_src):
    return opened_src.height,  opened_src.width,  opened_src.count

def read_raster_one_band_np(raster_path):
    with rasterio.open(raster_path) as src:
        indexes = src.indexes
        if len(indexes) != 1:
            raise IOError('error, only support one band')

        # data = src.read(indexes)   # output (1, 8249, 13524)
        data = src.read(1)       # output (8249, 13524)
        print(data.shape)
        # print(src.nodata)
        if src.nodata is not None:
            data[ data == src.nodata ] = np.nan
        return data

def save_numpy_array_to_rasterfile(numpy_array, save_path, ref_raster, format='GTiff', nodata=None):
    '''
    save a numpy to file, the numpy has the same projection and extent with ref_raster
    Args:
        numpy_array:
        save_path:
        ref_raster:
        format:

    Returns:

    '''
    if numpy_array.ndim == 2:
        band_count = 1
        height,width = numpy_array.shape
        # reshape to 3 dim, to write the disk
        numpy_array = numpy_array.reshape(band_count, height, width)
    elif numpy_array.ndim == 3:
        band_count, height,width = numpy_array.shape
    else:
        raise ValueError('only accept ndim is 2 or 3')

    dt = np.dtype(numpy_array.dtype)

    print('dtype:', dt.name)
    print(numpy_array.dtype)
    print('band_count,height,width',band_count,height,width)
    # print('saved numpy_array.shape',numpy_array.shape)

    with rasterio.open(ref_raster) as src:
        # test: save it to disk
        out_meta = src.meta.copy()
        out_meta.update({"driver": format,
                         "height": height,
                         "width": width,
                         "count":band_count,
                         "dtype": dt.name
                         })
        if nodata is not None:
            out_meta.update({"nodata": nodata})
        with rasterio.open(save_path, "w", **out_meta) as dest:
            dest.write(numpy_array)


    return True

def image_numpy_to_8bit(img_np, max_value, min_value, src_nodata=None, dst_nodata=None):
    '''
    convert float or 16 bit to 8bit,
    Args:
        img_np:  numpy array
        max_value:
        min_value:
        src_nodata:
        dst_nodata:  if output nodata is 0, then covert data to 1-255, if it's 255, then to 0-254

    Returns: new numpy array

    '''
    print('Convert to 8bit, old max, min: %.4f, %.4f'%(max_value, min_value))
    nan_loc = np.where(np.isnan(img_np))
    if nan_loc[0].size > 0:
        img_np = np.nan_to_num(img_np)

    img_np[img_np > max_value] = max_value
    img_np[img_np < min_value] = min_value

    if dst_nodata == 0:
        n_max, n_min = 255, 1
    elif dst_nodata == 255:
        n_max, n_min = 254, 0
    else:
        n_max, n_min = 255, 0

    # scale the grey values to 0 - 255 for better display
    k = (n_max - n_min)*1.0/(max_value - min_value)
    new_img_np = (img_np - min_value) * k + n_min
    new_img_np = new_img_np.astype(np.uint8)

    # replace nan data as nodata
    if nan_loc[0].size > 0:
        if dst_nodata is not None:
            new_img_np[nan_loc] = dst_nodata
        else:
            new_img_np[nan_loc] = n_min

    return new_img_np

def main():
    pass


if __name__=='__main__':
    main()

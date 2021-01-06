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


    pass


def main():
    pass


if __name__=='__main__':
    main()

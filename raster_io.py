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

from rasterio.coords import BoundingBox

def open_raster_read(raster_path):
    src = rasterio.open(raster_path)
    return src

def get_width_heigth_bandnum(opened_src):
    return opened_src.height,  opened_src.width,  opened_src.count

# def get_xres_yres(opened_src):
#     return opened_src.height,  opened_src.width,  opened_src.count

def get_xres_yres_file(file_path):
    with rasterio.open(file_path) as src:
        xres, yres  = src.res       # Returns the (width, height) of pixels in the units of its coordinate reference system.
        return xres, yres

def get_area_image_box(file_path):
    # get the area of an image coverage (including nodata area)
    with rasterio.open(file_path) as src:
        # the extent of the raster
        raster_bounds = src.bounds  # (left, bottom, right, top)
        height = raster_bounds.top - raster_bounds.bottom
        width = raster_bounds.right - raster_bounds.left
        return height*width

def get_image_bound_box(file_path, buffer=None):
    # get the bounding box: (left, bottom, right, top)
    with rasterio.open(file_path) as src:
        # the extent of the raster
        raster_bounds = src.bounds
        if buffer is not None:
            # Create new instance of BoundingBox(left, bottom, right, top)
            new_box_obj = BoundingBox(raster_bounds.left-buffer, raster_bounds.bottom-buffer,
                       raster_bounds.right+buffer, raster_bounds.top+ buffer)
            print(raster_bounds, new_box_obj)
            return new_box_obj
        return raster_bounds

def is_two_bound_disjoint(box1, box2):
    # box1 and box2: bounding box: (left, bottom, right, top)
    # Compare two bounds and determine if they are disjoint.
    # return True if bounds are disjoint, False if they are overlap
    return rasterio.coords.disjoint_bounds(box1,box2)

def is_two_image_disjoint(img1, img2, buffer=None):
    box1 = get_image_bound_box(img1, buffer=buffer)
    box2 = get_image_bound_box(img2, buffer=buffer)
    return is_two_bound_disjoint(box1,box2)


def read_oneband_image_to_1dArray(image_path,nodata=None, ignore_small=None):

    if os.path.isfile(image_path) is False:
        raise IOError("error, file not exist: " + image_path)

    with rasterio.open(image_path) as img_obj:
        # read the all bands (only have one band)
        indexes = img_obj.indexes
        if len(indexes) != 1:
            raise IOError('error, only support one band')

        data = img_obj.read(indexes)
        data_1d = data.flatten()  # convert to one 1d, row first.

        # input nodata
        if nodata is not None:
            data_1d = data_1d[data_1d != nodata]
        # the nodata in the image meta.
        if img_obj.nodata is not None:
            data_1d = data_1d[data_1d != img_obj.nodata]

        if ignore_small is not None:
            data_1d = data_1d[data_1d >= ignore_small ]

        return data_1d

def read_raster_all_bands_np(raster_path):

    with rasterio.open(raster_path) as src:
        indexes = src.indexes

        data = src.read(indexes)   # output (1, 8249, 13524), (band_count, height, width)

        # print(data.shape)
        # print(src.nodata)
        if src.nodata is not None and src.dtypes[0] == 'float32':
            data[ data == src.nodata ] = np.nan

        return data, src.nodata

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

def save_numpy_array_to_rasterfile(numpy_array, save_path, ref_raster, format='GTiff', nodata=None,
                                   compress=None, tiled=None, bigtiff=None):
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

        if compress is not None:
            out_meta.update(compress=compress)
        if tiled is not None:
            out_meta.update(tiled=tiled)
        if bigtiff is not None:
            out_meta.update(bigtiff=bigtiff)

        with rasterio.open(save_path, "w", **out_meta) as dest:
            dest.write(numpy_array)

    print('save to %s'%save_path)

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

#!/usr/bin/env python
# Filename: raster_io_test.py 
"""
introduction:

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 27 February, 2021
"""

import os, sys
import raster_io

import multiprocessing
from multiprocessing import Pool

def test_parallel_reading_images():
    # in some place, when calling get_valid_pixel_percentage in parallel (multiprocessing), after calculating,
    # the multiprocessing hang there, don't quick, like in a deadlock.

    # work_dir = os.path.expanduser('~/Data/Arctic/canada_arctic/DEM/WR_dem_diff/dem_tifs')
    # os.chdir(work_dir)
    # img_path = os.path.join(work_dir,'SETSM_WV01_20170630_1020010066903A00_1020010063388B00_seg1_2m_v3.0_dem_reg.tif')

    work_dir = os.path.expanduser('~/Data/Arctic/canada_arctic/DEM/WR_dem_diff')
    os.chdir(work_dir)
    img_path = os.path.join(work_dir,'WR_extent_date_diff_sub_1.tif')

    process_num = 4
    try_count = 200
    para_list = [ (img_path, None, '%d/%d'%(idx+1, try_count)) for idx in range(try_count) ]

    treadPool = Pool(process_num)
    results = treadPool.starmap(raster_io.get_valid_pixel_percentage, para_list)

    print('Done:')
    [print(res) for res in results]


if __name__ == '__main__':
    test_parallel_reading_images()
    pass
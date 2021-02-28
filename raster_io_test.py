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
import basic_src.io_function as io_function

import multiprocessing
from multiprocessing import Pool
from multiprocessing import Process

import time

def b_all_task_finish(all_tasks):
    for task in all_tasks:
        if task.is_alive():
            return False
    return True

def test_parallel_reading_images():
    # in some place, when calling get_valid_pixel_percentage in parallel (multiprocessing), after calculating,
    # the multiprocessing hang there, don't quick, like in a deadlock.
    # run this test on uist

    # work_dir = os.path.expanduser('~/Data/Arctic/canada_arctic/DEM/WR_dem_diff/dem_tifs')
    # os.chdir(work_dir)
    # img_path = os.path.join(work_dir,'SETSM_WV01_20170630_1020010066903A00_1020010063388B00_seg1_2m_v3.0_dem_reg.tif')

    # work_dir = os.path.expanduser('~/Data/Arctic/canada_arctic/DEM/WR_dem_diff')
    # os.chdir(work_dir)
    # img_path = os.path.join(work_dir,'WR_extent_date_diff_sub_1.tif')

    ## this example repeat the trouble: the multiprocessing hang there, don't quick after calcualting
    ## the image read into memory is quite large.
    work_dir = os.path.expanduser('~/Data/Arctic/canada_arctic/DEM/HotWC_dem_diff/dem_stripID_mosaic_sub_1')
    os.chdir(work_dir)
    img_path = os.path.join(work_dir,'20150407_103001003F724000_10300100405DA900.tif')
    ## tifs = io_function.get_file_list_by_ext('.tif',work_dir,bsub_folder=False)

    # 8, if we changed the process_num to 2, the problem also gone. 
    # it seems that when we have many process, and image is large (uist have limit memroy), 
    # then some process is dead, but multiprocessing hang in there to wait them back. 
    process_num = 2     
    try_count = 10
    para_list = [ (img_path, None, '%d/%d'%(idx+1, try_count)) for idx in range(try_count) ]

    # treadPool = Pool(process_num)
    # results = treadPool.starmap(raster_io.get_valid_pixel_percentage, para_list)

    # this parallel stategy, a few print Done, other processes did not return results
    sub_tasks = []
    for idx in range(try_count):
        sub_process = Process(target=raster_io.get_valid_pixel_percentage,args=(img_path, None, '%d/%d'%(idx+1, try_count)))
        sub_process.start()
        sub_tasks.append(sub_process)

    # check all the tasks already finished
    while b_all_task_finish(sub_tasks) is False:
        print('wait all tasks to finish')
        time.sleep(5)

    print('Done:')
    # [print(res) for res in results]


def test_reading_images_block_by_block():

    work_dir = os.path.expanduser('~/Data/Arctic/canada_arctic/DEM/WR_dem_diff/dem_tifs')
    os.chdir(work_dir)
    img_path = os.path.join(work_dir,'SETSM_WV01_20170630_1020010066903A00_1020010063388B00_seg1_2m_v3.0_dem_reg.tif')
    ## reading with blocks
    # valid_pixel_count, total_count, time cost 427551052 504329114 15.830054998397827
    # 84.77619874231571
    ## reading the entire images without blocks
    # valid_pixel_count, total_count, time cost 427551052 504329114 21.094736099243164
    # 84.77619874231571

    # work_dir = os.path.expanduser('~/Data/Arctic/canada_arctic/DEM/WR_dem_diff')
    # os.chdir(work_dir)
    # img_path = os.path.join(work_dir,'WR_extent_DEM_diff_sub_1_reg.tif')
    ## reading with blocks
    # valid_pixel_count, total_count, time cost 111300813 111559476 3.6818361282348633
    # 99.76813892528502
    ## reading the entire images without blocks
    # valid_pixel_count, total_count, time cost 111300813 111559476 4.6006247997283936
    # 99.76813892528502


    out = raster_io.get_valid_pixel_percentage(img_path)
    print(out)

if __name__ == '__main__':
    # test_parallel_reading_images()

    test_reading_images_block_by_block()

    pass
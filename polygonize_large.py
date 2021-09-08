#!/usr/bin/env python
# Filename: polygonize_large.py 
"""
introduction: polygonize a raster (large).
Using gdal_polygonize.py to rasterize raster data, but it's really slow when the rater is large and complex

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 06 September, 2021
"""


import os, sys
from optparse import OptionParser

import pandas as pd

import vector_gpd
import raster_io
import split_image
import timeTools
import vector_features
from datetime import datetime

import multiprocessing
from multiprocessing import Pool

import basic_src.io_function as io_function
import basic_src.map_projection as map_projection


def polygonzie_one_small_raster(idx, in_small_tif, patch_count, org_raster,connect8=True):

    print('tile: %d / %d' % (idx + 1, patch_count))
    return vector_gpd.raster2shapefile(in_small_tif,out_shp=None,connect8=connect8)

def read_polygons_from_small_patch(in_shp,in_raster):
    '''read polygons and seperate to touch and not touch image edge groups'''
    print(datetime.now(),'reading polygons to touch and not touch image edge group')
    polygons = vector_gpd.read_polygons_gpd(in_shp,b_fix_invalid_polygon=False)
    img_bound = raster_io.get_image_bound_box(in_raster)
    img_resx,img_resy = raster_io.get_xres_yres_file(in_raster)
    half_res = img_resx/2.0
    image_edge = vector_gpd.convert_image_bound_to_shapely_polygon(img_bound)

    polygons_buff = [ item.buffer(half_res) for item in polygons]   # buffer half pixel
    # polygons_touch_img_edge_index = []
    polygon_no_touch = []
    polygons_touch = []
    for idx, (polybuff,poly) in enumerate(zip(polygons_buff,polygons)):
        if polybuff.within(image_edge):
            polygon_no_touch.append(poly)
        else:
            # polygons_touch_img_edge_index.append(idx)
            polygons_touch.append(poly)

    # return polygons,polygons_touch_img_edge_index
    return polygon_no_touch,polygons_touch


def polygonzie_read_one_patch(idx, tif, patch_count,connect8):
    patch_shp = polygonzie_one_small_raster(idx, tif, patch_count, None, connect8=connect8)

    # read polygons,
    poly_no_touch, poly_touch = read_polygons_from_small_patch(patch_shp, tif)

    return poly_no_touch, poly_touch

def raster2shapefile_large(in_raster, working_dir, out_shp=None,connect8=True,process_num=1):

    if out_shp is None:
        out_shp = os.path.splitext(in_raster)[0] + '.shp'
    if os.path.isfile(out_shp):
        print('%s exists, skip'%out_shp)
        return out_shp

    if os.path.isdir(working_dir) is False:
        io_function.mkdir(working_dir)

    pre_name = os.path.splitext(os.path.basename(in_raster))[0]
    wkt = map_projection.get_raster_or_vector_srs_info_proj4(in_raster)

    # height, width, band_num, date_type = raster_io.get_height_width_bandnum_dtype(in_raster)
    # print('input image: height, width, band_num, date_type',height, width, band_num, date_type)

    out_raster_list = split_image.split_image(in_raster,working_dir,1024, 1024,adj_overlay_x=0,adj_overlay_y=0,out_format='GTIFF',pre_name=pre_name)
    patch_count = len(out_raster_list)
    patch_shps = []

    polygons_no_touch = []
    polygons_touch_edge = []

    if process_num == 1:
        for idx, tif in enumerate(out_raster_list):
            patch_shp = polygonzie_one_small_raster(idx, tif , patch_count, in_raster,connect8=connect8)
            patch_shps.append(patch_shp)

            # read polygons,
            poly_no_touch, poly_touch = read_polygons_from_small_patch(patch_shp, tif)
            polygons_no_touch.extend(poly_no_touch)
            polygons_touch_edge.extend(poly_touch)
    elif process_num > 1:
        theadPool = Pool(process_num)  # multi processes
        parameters_list = [(idx,tif, patch_count,True) for idx,tif in enumerate(out_raster_list)]
        results = theadPool.starmap(polygonzie_read_one_patch, parameters_list)  # need python3
        for poly_no_touch, poly_touch in results:
            polygons_no_touch.extend(poly_no_touch)
            polygons_touch_edge.extend(poly_touch)
        theadPool.close()
    else:
        raise ValueError('Wrong process number %s '%str(process_num))

    # save touch edge to file (for test)
    save_pd = pd.DataFrame({'Polygons':polygons_touch_edge})
    save_polygon_edge = os.path.splitext(out_shp)[0] + '_polyTouchEdge.gpkg'
    vector_gpd.save_polygons_to_files(save_pd,'Polygons',wkt,save_polygon_edge,format='GPKG')
    save_polygon_edge_2 = os.path.splitext(out_shp)[0] + '_polyTouchEdge.shp'
    vector_gpd.save_polygons_to_files(save_pd,'Polygons',wkt,save_polygon_edge_2)
    sys.exit(0)

    print('count of polygons touch patch edge', len(polygons_touch_edge))
    # merge all polygons touch edge
    print(timeTools.get_now_time_str(), 'start building adjacent_matrix')
    # if 'login' in machine_name or 'shas' in machine_name or 'sgpu' in machine_name:
    #     print('Warning, some problem of parallel running in build_adjacent_map_of_polygons on curc, but ok in my laptop and uist, change process_num = 1')
    #     process_num = 1

    polygons_touch_edge_buff = [item.buffer(0.1) for item in polygons_touch_edge]
    adjacent_matrix = vector_gpd.build_adjacent_map_of_polygons(polygons_touch_edge_buff, process_num=process_num)
    print(timeTools.get_now_time_str(), 'finish building adjacent_matrix')

    if adjacent_matrix is False:
        return False
    merged_polygons = vector_features.merge_touched_polygons(polygons_touch_edge, adjacent_matrix)
    print(timeTools.get_now_time_str(), 'finish merging touched polygons, get %d ones' % (len(merged_polygons)))

    # save all polygons to file
    polygons_no_touch.extend(merged_polygons)
    id_list = [idx for idx in range(len(polygons_no_touch)) ]

    save_pd = pd.DataFrame({'id':id_list,'Polygons':polygons_no_touch})
    vector_gpd.save_polygons_to_files(save_pd,'Polygons',wkt,out_shp)



def test_raster2shapefile_large():
    in_tif = os.path.expanduser('~/Data/dem_processing/grid_9053_tmp_files/20140701_dem_slope_bin.tif')
    working_dir = os.path.expanduser('~/Data/dem_processing/grid_9053_tmp_files/20140701_dem_slope_bin_patches')

    out_shp = os.path.expanduser('~/Data/dem_processing/grid_9053_tmp_files/20140701_dem_slope_bin_patches_all.shp')
    process_num = 12
    raster2shapefile_large(in_tif, working_dir, out_shp=out_shp, connect8=True, process_num=process_num)


def test_read_polygons_from_small_patch():
    data_dir = os.path.expanduser('~/Data/dem_processing/grid_9053_tmp_files/20140701_dem_slope_bin_patches')
    in_shp = os.path.join(data_dir,'20140701_dem_slope_bin_p_0.shp')
    in_raster = os.path.join(data_dir,'20140701_dem_slope_bin_p_0.tif')
    polygons, index = read_polygons_from_small_patch(in_shp, in_raster)
    print('polygon count:', len(polygons))
    print(' touch polygon count:', len(index))
    print(index)


def test_build_adjacent_matrix_pygeo():
    vector_path = os.path.expanduser('~/Data/dem_processing/grid_9053_tmp_files/20140701_dem_slope_bin_patches_all_polyTouchEdge.gpkg')
    polygons = vector_gpd.read_polygons_gpd(vector_path,b_fix_invalid_polygon=False)
    print('read %d polygons'%len(polygons))
    # polygons = [item.buffer(1.0) for item in polygons]    # for complex polygons, buffer take a long time.
    from pygeos import area, intersection,from_shapely,touches
    import numpy as np
    geo_polygons = from_shapely(polygons)
    print(geo_polygons)

    # inter_matrix = intersection(geo_polygons[:, np.newaxis], geo_polygons[np.newaxis, :])
    # print(inter_matrix)

    # print(touches(geo_polygons[:, np.newaxis], geo_polygons[np.newaxis, :]))
    print(touches(geo_polygons, geo_polygons))

    # area_matrix = area(intersection(geo_polygons[:, np.newaxis], geo_polygons[np.newaxis, :]))
    # print(area_matrix)

    # not working, there are some invalid polgyongs.
    # buffer operation for polgyons take a lot of time, could be due to the complex polygons.


def main(options, args):

    work_dir = options.work_dir
    in_raster = args[0]
    save_path = options.save_path
    process_num = options.process_num

    # note: Sep 7, 2021. Not working. the last idea to try: need the row and coloumn for each patch,
    # then merge polygons one patch by patch.

    return raster2shapefile_large(in_raster, work_dir, out_shp=save_path, connect8=True,process_num=process_num)


if __name__ == '__main__':

    # test_raster2shapefile_large()
    # test_read_polygons_from_small_patch()
    test_build_adjacent_matrix_pygeo()
    sys.exit(0)

    usage = "usage: %prog [options] raster_path "
    parser = OptionParser(usage=usage, version="1.0 2021-09-06")
    parser.description = 'Introduction: polygonzie large rasters '

    parser.add_option("-d", "--work_dir",
                      action="store", dest="save_dir", default='patches_shp',
                      help="the folder to save intermediate files")

    parser.add_option("-s", "--save_path",
                      action="store", dest="save_path",
                      help="the save path of vector file")

    parser.add_option("", "--process_num",
                      action="store", dest="process_num", type=int, default=4,
                      help="number of processes to create the mosaic")

    (options, args) = parser.parse_args()

    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)

    main(options, args)
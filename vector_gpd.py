#!/usr/bin/env python
# Filename: vector_gpd 
"""
introduction: similar to vector_features.py, by use geopandas to read and write shapefile

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 08 December, 2019
"""

import os,sys
from optparse import OptionParser


# import these two to make sure load GEOS dll before using shapely
import shapely
from shapely.geometry import mapping # transform to GeJSON format
import geopandas as gpd

import basic_src.basic as basic

def read_polygons_json(polygon_shp, no_json=False):
    '''
    read polyogns and convert to json format
    :param polygon_shp: polygon in projection of EPSG:4326
    :param no_json: True indicate not json format
    :return:
    '''

    # check projection
    shp_args_list = ['gdalsrsinfo', '-o', 'EPSG', polygon_shp]
    epsg_str = basic.exec_command_args_list_one_string(shp_args_list)
    epsg_str = epsg_str.decode().strip()  # byte to str, remove '\n'
    if epsg_str != 'EPSG:4326':
        raise ValueError('Current support shape file in projection of EPSG:4326, but the input has projection of %s'%epsg_str)

    shapefile = gpd.read_file(polygon_shp)
    polygons = shapefile.geometry.values

    # # check invalidity of polygons
    invalid_polygon_idx = []
    # for idx, geom in enumerate(polygons):
    #     if geom.is_valid is False:
    #         invalid_polygon_idx.append(idx + 1)
    # if len(invalid_polygon_idx) > 0:
    #     raise ValueError('error, polygons %s (index start from 1) in %s are invalid, please fix them first '%(str(invalid_polygon_idx),polygon_shp))

    # fix invalid polygons
    for idx in range(0,len(polygons)):
        if polygons[idx].is_valid is False:
            invalid_polygon_idx.append(idx + 1)
            polygons[idx] = polygons[idx].buffer(0.000001)  # trying to solve self-intersection
    if len(invalid_polygon_idx) > 0:
        basic.outputlogMessage('Warning, polygons %s (index start from 1) in %s are invalid, fix them by the buffer operation '%(str(invalid_polygon_idx),polygon_shp))

    if no_json:
        return polygons
    else:
        # convert to json format
        polygons_json = [ mapping(item) for item in polygons]

    return polygons_json

def main(options, args):
    pass



if __name__=='__main__':
    usage = "usage: %prog [options] input_path output_file"
    parser = OptionParser(usage=usage, version="1.0 2016-10-26")
    parser.add_option("-p", "--para",
                      action="store", dest="para_file",
                      help="the parameters file")
    # parser.add_option("-s", "--used_file", action="store", dest="used_file",
    #                   help="the selectd used files,only need when you set --action=2")
    # parser.add_option('-o', "--output", action='store', dest="output",
    #                   help="the output file,only need when you set --action=2")

    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 2:
        parser.print_help()
        sys.exit(2)
    main(options, args)

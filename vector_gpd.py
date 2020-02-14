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
from shapely.geometry import Point

import math

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

def read_polygons_gpd(polygon_shp):
    '''
    read polyogns using geopandas
    :param polygon_shp: polygon in projection of EPSG:4326
    :param no_json: True indicate not json format
    :return:
    '''

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

    return polygons

def calculate_polygon_shape_info(polygon_shapely):
    '''
    calculate the shape information of a polygon, including area, perimeter, circularity,
    WIDTH and HEIGHT based on minimum_rotated_rectangle,
    :param polygon_shapely: a polygon (shapely object)
    :return:
    '''
    shape_info = {}
    shape_info['INarea'] = polygon_shapely.area
    shape_info['INperimete']  = polygon_shapely.length

    # circularity
    circularity = (4 * math.pi *  polygon_shapely.area / polygon_shapely.length** 2)
    shape_info['circularit'] = circularity

    minimum_rotated_rectangle = polygon_shapely.minimum_rotated_rectangle

    points = list(minimum_rotated_rectangle.boundary.coords)
    point1 = Point(points[0])
    point2 = Point(points[1])
    point3 = Point(points[2])
    width = point1.distance(point2)
    height = point2.distance(point3)

    shape_info['WIDTH'] = width
    shape_info['HEIGHT'] = height
    if width > height:
        shape_info['ratio_w_h'] = height / width
    else:
        shape_info['ratio_w_h'] = width / height

    #added number of holes
    shape_info['hole_count'] = len(list(polygon_shapely.interiors))

    return shape_info


def save_polygons_to_files(data_frame, geometry_name, wkt_string, save_path):
    '''
    :param data_frame: include polygon list and the corresponding attributes
    :param geometry_name: dict key for the polgyon in the DataFrame
    :param wkt_string: wkt string (projection)
    :param save_path: save path
    :return:
    '''
    # data_frame[geometry_name] = data_frame[geometry_name].apply(wkt.loads)
    poly_df = gpd.GeoDataFrame(data_frame, geometry=geometry_name)
    poly_df.crs = wkt_string # or poly_df.crs = {'init' :'epsg:4326'}
    poly_df.to_file(save_path, driver='ESRI Shapefile')

    return True



def main(options, args):

    # test reading polygons with holes
    polygons = read_polygons_gpd(args[0])
    for idx, polygon in enumerate(polygons):
        if idx == 268:
            test = 1
            # print(polygon)
        print(idx, list(polygon.interiors))
        for inPoly in list(polygon.interiors):      # for holes
            print(inPoly)


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

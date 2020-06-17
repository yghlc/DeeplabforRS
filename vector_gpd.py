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
from shapely.geometry import MultiPolygon
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd

import math

import basic_src.basic as basic

import basic_src.map_projection as map_projection

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
    polygons = fix_invalid_polygons(polygons,polygon_shp)

    if no_json:
        return polygons
    else:
        # convert to json format
        polygons_json = [ mapping(item) for item in polygons]

    return polygons_json

def fix_invalid_polygons(polygons, polygon_shp, buffer_size = 0.000001):
    '''
    fix invalid polygon by using buffer operation.
    :param polygons: polygons in shapely format
    :param polygon_shp: shapefile path where the polygons are from
    :param buffer_size: buffer size
    :return: polygons after checking invalidity
    '''
    invalid_polygon_idx = []
    for idx in range(0,len(polygons)):
        if polygons[idx].is_valid is False:
            invalid_polygon_idx.append(idx + 1)
            polygons[idx] = polygons[idx].buffer(buffer_size)  # trying to solve self-intersection
    if len(invalid_polygon_idx) > 0:
        basic.outputlogMessage('Warning, polygons %s (index start from 1) in %s are invalid, fix them by the buffer operation '%(str(invalid_polygon_idx),polygon_shp))

    return polygons

def read_lines_gpd(lines_shp):
    shapefile = gpd.read_file(lines_shp)
    lines = shapefile.geometry.values
    # check are lines
    return lines

def find_one_line_intersect_Polygon(polygon, line_list, line_check_list):
    for idx, (line, b_checked) in enumerate(zip(line_list,line_check_list)):
        if b_checked:
            continue
        if polygon.intersection(line).is_empty is False:
            line_check_list[idx] = True
            return line
    return None

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
    polygons = fix_invalid_polygons(polygons,polygon_shp)

    return polygons

def read_attribute_values_list(polygon_shp, field_name):
    '''
    read the attribute value to a list
    :param polygon_shp:
    :param field_name:
    :return: a list containing the attribute values
    '''

    shapefile = gpd.read_file(polygon_shp)
    attribute_values = shapefile[field_name]

    return attribute_values.tolist()


def remove_polygon_equal(shapefile,field_name, expect_value, b_equal, output):
    '''
    remove polygons the the attribute value is not equal to a specific value
    :param shapefile:
    :param field_name:
    :param threshold:
    :param b_equal: if True, remove records not equal to expect_value, otherwise, remove the one equal to expect_value
    :param output:
    :return:
    '''

    shapefile = gpd.read_file(shapefile)

    remove_count = 0

    for idx,row in shapefile.iterrows():

        # polygon = row['geometry']
        # go through post-processing to decide to keep or remove it
        if b_equal:
            if row[field_name] != expect_value:
                shapefile.drop(idx, inplace=True)
                remove_count += 1
        else:
            if row[field_name] == expect_value:
                shapefile.drop(idx, inplace=True)
                remove_count += 1

    basic.outputlogMessage('remove %d polygons based on %s, remain %d ones saving to %s' %
                           (remove_count, field_name, len(shapefile.geometry.values), output))
    # save results
    shapefile.to_file(output, driver='ESRI Shapefile')

def remove_polygon_index_string(shapefile,field_name, index_list, output):
    '''
    remove polygons the the attribute value is not equal to a specific value
    :param shapefile:
    :param field_name:
    :param threshold:
    :param b_equal: if True, remove records not equal to expect_value, otherwise, remove the one equal to expect_value
    :param output:
    :return:
    '''
    if len(index_list) < 1:
        raise ValueError('Wrong input index_list, it size is zero')

    shapefile = gpd.read_file(shapefile)

    remove_count = 0

    for idx,row in shapefile.iterrows():

        # polygon = row['geometry']
        # go through post-processing to decide to keep or remove it
        idx_string = row[field_name]
        num_list =  [ int(item) for item in idx_string.split('_')]

        # if all the index in index_list found in num_list, then keep it, otherwise, remove it
        for index in index_list:
            if index not in num_list:
                shapefile.drop(idx, inplace=True)
                remove_count += 1
                break

    basic.outputlogMessage('remove %d polygons based on %s, remain %d ones saving to %s' %
                           (remove_count, field_name, len(shapefile.geometry.values), output))
    # save results
    shapefile.to_file(output, driver='ESRI Shapefile')

def remove_polygons_not_in_range(shapefile,field_name, min_value, max_value,output):
    '''
    remove polygon not in range (min, max]
    :param shapefile:
    :param field_name:
    :param min_value:
    :param max_value:
    :param output:
    :return:
    '''
    # read polygons as shapely objects
    shapefile = gpd.read_file(shapefile)

    remove_count = 0

    for idx, row in shapefile.iterrows():

        # polygon = row['geometry']
        # go through post-processing to decide to keep or remove it
        if row[field_name] < min_value or row[field_name] >= max_value:
            shapefile.drop(idx, inplace=True)
            remove_count += 1

    basic.outputlogMessage('remove %d polygons based on %s, remain %d ones saving to %s' %
                           (remove_count, field_name, len(shapefile.geometry.values), output))
    # save results
    shapefile.to_file(output, driver='ESRI Shapefile')


def remove_polygons(shapefile,field_name, threshold, bsmaller,output):
    '''
    remove polygons based on attribute values
    :param shapefile:
    :param field_name:
    :param threshold:
    :param bsmaller:
    :param output:
    :return:
    '''
    # another version
    # operation_obj = shape_opeation()
    # if operation_obj.remove_shape_baseon_field_value(shapefile, output, field_name, threshold, smaller=bsmaller) is False:
    #     return False

    # read polygons as shapely objects
    shapefile = gpd.read_file(shapefile)

    remove_count = 0

    for idx,row in shapefile.iterrows():

        # polygon = row['geometry']
        # go through post-processing to decide to keep or remove it

        if bsmaller:
            if row[field_name] < threshold:
                shapefile.drop(idx, inplace=True)
                remove_count += 1
        else:
            if row[field_name] >= threshold:
                shapefile.drop(idx, inplace=True)
                remove_count += 1

    basic.outputlogMessage('remove %d polygons based on %s, remain %d ones saving to %s' %
                           (remove_count, field_name, len(shapefile.geometry.values), output))
    # save results
    shapefile.to_file(output, driver='ESRI Shapefile')

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

def remove_narrow_parts_of_a_polygon(shapely_polygon, rm_narrow_thr):
    '''
    try to remove the narrow (or thin) parts of a polygon by using buffer opeartion
    :param shapely_polygon: a shapely object, Polygon or MultiPolygon
    :param rm_narrow_thr: how narrow
    :return: the shapely polygon, multipolygons or polygons
    '''

    # A positive distance has an effect of dilation; a negative distance, erosion.
    # object.buffer(distance, resolution=16, cap_style=1, join_style=1, mitre_limit=5.0)

    enlarge_factor = 1.6
    # can return multiple polygons
    # remain_polygon_parts = shapely_polygon.buffer(-rm_narrow_thr)
    # remain_polygon_parts = shapely_polygon.buffer(-rm_narrow_thr).buffer(rm_narrow_thr * enlarge_factor)
    remain_polygon_parts = shapely_polygon.buffer(-rm_narrow_thr).buffer(rm_narrow_thr * enlarge_factor).intersection(shapely_polygon)

    return remain_polygon_parts

def remove_narrow_parts_of_polygons_shp(input_shp,out_shp,rm_narrow_thr):
    # read polygons as shapely objects
    shapefile = gpd.read_file(input_shp)

    attribute_names = None
    new_polygon_list = []
    polygon_attributes_list = []  # 2d list

    for idx, row in shapefile.iterrows():
        if idx==0:
            attribute_names = row.keys().to_list()[:-1]  # the last one is 'geometry'
        print('removing narrow parts of %dth polygon (total: %d)'%(idx+1,len(shapefile.geometry.values)))
        shapely_polygon = row['geometry']
        out_polygon = remove_narrow_parts_of_a_polygon(shapely_polygon, rm_narrow_thr)
        # if out_polygon.is_empty is True:
        #     print(idx, out_polygon)
        if out_polygon.is_empty is True:
            basic.outputlogMessage('Warning, remove %dth (0 index) polygon in %s because it is empty after removing narrow parts'%
                                   (idx, os.path.basename(input_shp)))
            # continue, don't save
            # shapefile.drop(idx, inplace=True),
        else:
            new_polygon_list.append(out_polygon)
            attributes = [row[key] for key in attribute_names]
            polygon_attributes_list.append(attributes)        # last one is 'geometry'
            # copy attributes

    save_polyons_attributes = {}
    for idx, attribute in enumerate(attribute_names):
        # print(idx, attribute)
        values = [item[idx] for item in polygon_attributes_list]
        save_polyons_attributes[attribute] = values

    save_polyons_attributes["Polygons"] = new_polygon_list
    polygon_df = pd.DataFrame(save_polyons_attributes)

    basic.outputlogMessage('After removing the narrow parts, obtaining %d polygons'%len(new_polygon_list))
    basic.outputlogMessage('will be saved to %s'%out_shp)
    wkt_string = map_projection.get_raster_or_vector_srs_info_wkt(input_shp)
    return save_polygons_to_files(polygon_df, 'Polygons', wkt_string, out_shp)

def polygons_to_a_MultiPolygon(polygon_list):
    if isinstance(polygon_list,list) is False:
        raise ValueError('the input is a not list')
    if len(polygon_list) < 1:
        raise ValueError('There is no polygon in the input')
    return MultiPolygon(polygon_list)

def main(options, args):

    # ###############################################################
    # # test reading polygons with holes
    # polygons = read_polygons_gpd(args[0])
    # for idx, polygon in enumerate(polygons):
    #     if idx == 268:
    #         test = 1
    #         # print(polygon)
    #     print(idx, list(polygon.interiors))
    #     for inPoly in list(polygon.interiors):      # for holes
    #         print(inPoly)

    ###############################################################
    # test thinning a polygon
    input_shp = args[0]
    save_shp = args[1]
    # out_polygons_list = []
    # polygons = read_polygons_gpd(input_shp)
    # for idx, polygon in enumerate(polygons):
    #     # print(idx, polygon)
    #
    #     out_polygons = remove_narrow_parts_of_a_polygon(polygon,1.5)
    #     # save them
    #     out_polygons_list.append(out_polygons)
    #     print(idx)
    # import pandas as pd
    # import basic_src.map_projection as map_projection
    # out_polygon_df = pd.DataFrame({'out_Polygons': out_polygons_list
    #                             })
    #
    # wkt_string = map_projection.get_raster_or_vector_srs_info_wkt(input_shp)
    # save_polygons_to_files(out_polygon_df,'out_Polygons', wkt_string, save_shp)

    remove_narrow_parts_of_polygons_shp(input_shp,save_shp, 1.5)


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

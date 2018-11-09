#!/usr/bin/env python
# Filename: read_raster_for_shapefile.py
"""
introduction:

authors: Yan
email: yan_hu@hotmail.com
add time: 29 July, 2018
"""

import os, sys
from optparse import OptionParser
import basic_src
from basic_src import io_function
from basic_src import basic
from basic_src import RSImage

import shapefile
# import vector_features

# from vector_features import shape_operation


def read_start_end_point_length_of_a_line(shape_file):
    """

    Args:
        shape_file:

    Returns:

    """

    if io_function.is_file_exist(shape_file) is False:
        return False

    try:
        org_obj = shapefile.Reader(shape_file)
    except:
        basic.outputlogMessage(str(IOError))
        return False

    # Create a new shapefile in memory
    # w = shapefile.Writer()
    # w.shapeType = org_obj.shapeType

    org_records = org_obj.records()
    if (len(org_records) < 1):
        basic.outputlogMessage('error, no record in shape file ')
        return False

    # Copy over the geometry without any changes
    shapes_list = org_obj.shapes()
    if len(shapes_list) < 1:
        raise ValueError("No shape")

    # define list
    start_point = []
    end_point = []
    length = []

    # read length (second)
    for record in org_records:
        length.append(record[1])

    for shape in shapes_list:
        # print(shape)
        # print(shape)
        print(shape.points)
        points = shape.points
        if len(points) != 2:
            raise ValueError("Not 2 points in a line")

        start_point.append(points[0])
        end_point.append(points[1])

    return start_point, end_point, length


def read_dem_basedON_location(x, y, dem_raster):
    # return RSImage.get_image_location_value(dem_raster,x,y,'lon_lat_wgs84',1)
    return RSImage.get_image_location_value(dem_raster, x, y, 'lon_lat_wgs84', 1)


def calculate_polygon_topography(polygons_shp, dem_file):
    """

    Args:
        polygons_shp:
        dem_file:

    Returns:

    """
    if io_function.is_file_exist(polygons_shp) is False:
        return False
    operation_obj = shape_opeation()

    # all_touched: bool, optional
    #     Whether to include every raster cell touched by a geometry, or only
    #     those having a center point within the polygon.
    #     defaults to `False`
    #   Since the dem usually is coarser, so we set all_touched = True
    all_touched = True

    # #DEM
    if io_function.is_file_exist(dem_file):
        stats_list = ['min', 'max', 'mean', 'std']  # ['min', 'max', 'mean', 'count','median','std']
        if operation_obj.add_fields_from_raster(polygons_shp, dem_file, "dem", band=1, stats_list=stats_list,
                                                all_touched=all_touched) is False:
            return False
    else:
        basic.outputlogMessage("warning, DEM file not exist, skip the calculation of DEM information")

    return True


def main(options, args):
    shp_file = args[0]
    raster = args[1]

    # read shape file
    start_point, end_point, length = read_start_end_point_length_of_a_line(shp_file)

    # get value of points
    shape_count = len(start_point)

    # create a file recording the altitudes
    f = open("altitude", "w+")

    for idx in range(shape_count):
        # read value of start point
        start_value = read_dem_basedON_location(start_point[idx][0], start_point[idx][1], raster)
        # read value of end point
        end_value = read_dem_basedON_location(end_point[idx][0], end_point[idx][1], raster)

        print(start_value, end_value)
        content = (start_value, end_value)

        f.write(content)
        f.close()

        # calculate



    pass


if __name__ == '__main__':
    usage = "usage: %prog [options] shp raster_file"
    parser = OptionParser(usage=usage, version="1.0 2017-7-24")
    parser.description = 'Introduction:   '

    parser.add_option("-p", "--para",
                      action="store", dest="para_file",
                      help="the parameters file")

    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 2:
        parser.print_help()
        sys.exit(2)
    # ## set parameters files
    # if options.para_file is None:
    #     print('error, no parameters file')
    #     parser.print_help()
    #     sys.exit(2)
    # else:
    #     parameters.set_saved_parafile_path(options.para_file)

    main(options, args)

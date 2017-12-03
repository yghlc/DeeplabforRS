#!/usr/bin/env python
# Filename: extract_target_imgs 
"""
introduction:

    This script extracts patches with the target in the center base on target polyogns in shapefile.

    It can also perform basic data augmentation (rotations and flips).

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 18 July, 2017
"""



import sys,os,subprocess
from optparse import OptionParser

sys.path.append('basic_src')

import basic_src.io_function as io_function
import vector_features
import basic_src.RSImageProcess as RSImageProcess

#pyshp library
import shapefile

# import shapely
from shapely.geometry import Polygon

def get_polygons(shp_path):
    if os.path.isfile(shp_path) is False:
        print('Error, File: %s not exist'%shp_path)
        return False

    try:
        shp_obj = shapefile.Reader(shp_path)
    except IOError:
        print("Read file: %s failed: "%shp_path + str(IOError))
        return False

    if shp_obj.shapeType != 5:
        print('It is not a polygon shapefile')
        return False

    shapes_list = shp_obj.shapes()
    return shapes_list

def save_polygons_to_shp(polygon_list, base_shp,folder):
    if len(polygon_list) < 1:
        print ('Error, there is no polygon in the list')
        return False

    try:
        shp_obj = shapefile.Reader(base_shp)
    except IOError:
        print("Read file: %s failed: "%base_shp + str(IOError))
        return False

    save_shp_list = []

    save_id = 0
    for polygon in polygon_list:
        w = shapefile.Writer()
        w.shapeType = shp_obj.shapeType

        filename = os.path.join(folder, os.path.splitext(os.path.basename(base_shp))[0] + '_'+str(save_id)+'.shp')
        if os.path.isfile(filename) is False:
            w.field('id')
            w._shapes.append(polygon)
            w.record(save_id)

            # copy prj file
            org_prj = os.path.splitext(base_shp)[0] + ".prj"
            out_prj = os.path.splitext(filename)[0] + ".prj"
            io_function.copy_file_to_dst(org_prj, out_prj, overwrite=True)

            # save to file
            w.save(filename)
        else:
            print ('warning: %s already exist, skip'%filename)

        save_id += 1
        save_shp_list.append(filename)

    return save_shp_list

def get_layer_extent(polygon_file):
    try:
        shp_obj = shapefile.Reader(polygon_file)
    except IOError:
        print("Read file: %s failed: "%polygon_file + str(IOError))
        return False

    extent = shp_obj.bbox

    return extent

def main(options, args):

    if options.s_width is None:
        patch_width = 1024
    else:
        patch_width = int(options.s_width)
    if options.s_height is None:
        patch_height = 1024
    else:
        patch_height = int(options.s_width)

    if options.out_dir is None:
        out_dir = "extract_dir"
    else:
        out_dir = options.out_dir

    if options.dstnodata is None:
        dstnodata = 255
    else:
        dstnodata = options.dstnodata


    bSub_rect = options.rectangle

    if os.path.isdir(out_dir) is False:
        os.makedirs(out_dir)


    buffer_size = 10 # buffer size is 10 meters (in the projection)
    if options.bufferSize is not None:
        buffer_size = options.bufferSize


    shp_path = args[0]
    image_path = args[1]

    # get polygons
    polygons = get_polygons(shp_path)

    # buffer polygons (dilation)
    poly_geos =  [vector_features.shape_from_pyshp_to_shapely(pyshp_polygon) for pyshp_polygon in polygons ]
    poly_geos_buffer = [ shapely_obj.buffer(buffer_size) for shapely_obj in  poly_geos ]

    #save each polygon to the folder
    poly_pyshp = [vector_features.shape_from_shapely_to_pyshp(item) for item in poly_geos_buffer]

    polygon_files = save_polygons_to_shp(poly_pyshp,shp_path,out_dir)

    # print (polygon_files)
    # subset image based on polygon
    save_id = 0
    for polygon in polygon_files:
        Outfilename = os.path.join(out_dir,os.path.splitext(os.path.basename(image_path))[0] + '_'+str(save_id)+'.tif')
        if bSub_rect is True:
            extent = get_layer_extent(polygon)
            RSImageProcess.subset_image_projwin(Outfilename,image_path,extent[0],extent[3],extent[2],extent[1],dst_nondata=dstnodata)
        else:
            RSImageProcess.subset_image_by_shapefile(image_path,polygon,Outfilename,True)
        save_id += 1

    pass


if __name__ == "__main__":
    usage = "usage: %prog [options] target_shp image"
    parser = OptionParser(usage=usage, version="1.0 2017-7-15")
    parser.description = 'Introduction: Extract patches based on polygons in shapefile from a large image \n ' \
                         'The image and shape file should have the same projection'
    parser.add_option("-W", "--s_width",
                      action="store", dest="s_width",
                      help="the width of wanted patch")
    parser.add_option("-H", "--s_height",
                      action="store", dest="s_height",
                      help="the height of wanted patch")
    parser.add_option("-b", "--bufferSize",
                      action="store", dest="bufferSize",type=float,
                      help="buffer size is in the projection, normally, it is based on meters")
    parser.add_option("-o", "--out_dir",
                      action="store", dest="out_dir",
                      help="the folder path for saving output files")
    parser.add_option("-n", "--dstnodata",
                      action="store", dest="dstnodata",
                      help="the nodata in output images")
    parser.add_option("-r", "--rectangle",
                      action="store_true", dest="rectangle",default=False,
                      help="whether use the rectangular extent of the polygon")


    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)

    # if options.para_file is None:
    #     basic.outputlogMessage('error, parameter file is required')
    #     sys.exit(2)

    main(options, args)

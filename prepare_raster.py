#!/usr/bin/env python
# Filename: prepare_raster 
"""
introduction: Preparing the whole training label images, divide the images to patches with the same size

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 14 November, 2017
"""

from optparse import OptionParser
import basic_src.basic as basic
import basic_src.io_function as io_function
import os,sys


# import  parameters
import vector_features
from vector_features import shape_opeation
import parameters

import classLabel
import basic_src.RSImageProcess as RSImageProcess

def convert_training_examples_from_shp_to_raster(shp_path,raster_path):
    """
    convert training examples which stored in shape file to a raster file,
    so these training examples can be shared by other shape file
    :param shp_path: shape file path
    :param raster_path: raster data path (the output data type is Byte)
    :return:True if successful, False otherwise
    """
    if io_function.is_file_exist(shp_path) is False:
        return False

    # convert class label (string) to class index (integer)
    class_int_field = 'class_int'
    class_label_field = 'class'
    class_int_list = []
    shp_operation_obj = shape_opeation()
    if shp_operation_obj.has_field(shp_path,class_int_field) is False:
        if shp_operation_obj.has_field(shp_path,class_label_field) is False:
            basic.outputlogMessage('%s do not contain training examples'%shp_path)
        else:
            # convert class label (string) to class index (integer) and create a new field name 'class_int'
            attribute = ['class']
            class_label_list = shp_operation_obj.get_shape_records_value(shp_path,attribute)
            classLabel.output_classLabel_to_txt('class_label_index.txt')
            for label in class_label_list:
                class_int_list.append(classLabel.get_class_index(label[0]))
            shp_operation_obj.add_one_field_records_to_shapefile(shp_path,class_int_list,class_int_field)

    # check again whether there is 'class_int'
    if shp_operation_obj.has_field(shp_path, class_int_field) is False:
        basic.outputlogMessage("There is not class_int field in the shape file")
        assert False

    # convert training example in shape file to raster
    res = parameters.get_input_image_rescale()
    layername =  os.path.splitext(os.path.basename(shp_path))[0]
    args_list = ['gdal_rasterize', '-a', class_int_field, '-ot', 'Byte', \
                 '-tr',str(res),str(res),'-l',layername,shp_path,raster_path]
    result = basic.exec_command_args_list_one_file(args_list,raster_path)
    if os.path.getsize(result) < 1:
        return False
    return True

def only_keep_one_class(label_raster,output_raster, class_index=1):

    if io_function.is_file_exist(label_raster) is False:
        return False

    # convert training example in shape file to raster

    ### args_list to run the command line of gdal_calc.py result in error, it strange 2017-11-14
    # gdal_calc.py -A raster_class.tif  --outfile=raster_class_version_BLH_0.6m.tif --calc="A==1"  --debug --type='Byte' --overwrite
    # args_list = ['gdal_calc.py', '-A',label_raster, '--outfile='+output_raster, \
    #              '--calc='+'\"A=='+str(class_index)+'\"','--debug','--type=\'Byte\'','--overwrite']
    # result = basic.exec_command_args_list_one_file(args_list,output_raster)

    cmd_str= 'gdal_calc.py'+' '+ '-A' +' '+ label_raster+ ' '+  '--outfile='+output_raster +' '+ \
                 '--calc='+'\"A=='+str(class_index)+'\"' +' '+ '--debug' +' '+ '--type=\'Byte\''+' '+ '--overwrite'

    result = basic.exec_command_string_one_file(cmd_str,output_raster)

    if os.path.getsize(result) < 1:
        basic.outputlogMessage("Error in only_keep_one_class")
        assert False

    return True

def main(options, args):

    input_shp = args[0]
    output_raster = args[1]

    if io_function.is_file_exist(input_shp) is False:
        return False

    all_class_raster = io_function.get_name_by_adding_tail(output_raster,'AllClass')

    if convert_training_examples_from_shp_to_raster(input_shp, all_class_raster) is False:
        basic.outputlogMessage("Producing the label images from training polygons is Falild")
        return False
    else:
        basic.outputlogMessage("Done: Producing the label images from training polygons, output: %s"%all_class_raster )

    #only keep target (gully or others) label
    one_class_raster=io_function.get_name_by_adding_tail(output_raster,'oneClass')
    if only_keep_one_class(all_class_raster,one_class_raster,class_index=1) is False:
        return False

    # crop the label image to have the same 2D dimension with the training images
    baseimage = parameters.get_input_image_path()
    if RSImageProcess.subset_image_baseimage(output_raster,one_class_raster,baseimage) is False:
        basic.outputlogMessage("Error: subset_image_baseimage Failed")
        return False

    return True

if __name__=='__main__':
    usage = "usage: %prog [options] shapefile output_raster"
    parser = OptionParser(usage=usage, version="1.0 2017-7-24")
    parser.description = 'Introduction: Preparing training label images, and so on'
    parser.add_option("-p", "--para",
                      action="store", dest="para_file",
                      help="the parameters file")

    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 2:
        parser.print_help()
        sys.exit(2)
    ## set parameters files
    if options.para_file is None:
        print('error, no parameters file')
        parser.print_help()
        sys.exit(2)
    else:
        parameters.set_saved_parafile_path(options.para_file)

    main(options, args)

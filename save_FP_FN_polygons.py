#!/usr/bin/env python
# Filename: save_FP_FN_polygons 
"""
introduction: save false positive and false negative polygons in the mapped polygons

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 03 September, 2020
"""

from optparse import OptionParser
import os,sys
import basic_src.basic as basic
import basic_src.io_function as io_function
import parameters

import vector_features
from vector_gpd import remove_polygons_based_values


def save_false_positve_and_false_negative(result_shp,val_shp,para_file):
    """
    save false positive and false negative polygons in the mapped polygon based on IOU values
    :param result_shp: result shape file containing mapped polygons
    :param val_shp: shape file containing validation polygons
    :return:
    """

    assert io_function.is_file_exist(result_shp)
    assert io_function.is_file_exist(val_shp)
    basic.outputlogMessage('Input mapping result: %s'%result_shp)
    basic.outputlogMessage('Input ground truth: %s'%val_shp)

    IOU_threshold = parameters.get_IOU_threshold(parafile=para_file)
    basic.outputlogMessage('IOU threshold is: %f' % IOU_threshold)

    # calcuate IOU
    IOU_mapped_polygons = vector_features.calculate_IoU_scores(result_shp,val_shp)
    save_FP_path = io_function.get_name_by_adding_tail(result_shp,'FP')
    # set False, remove greater than the threshold one
    remove_polygons_based_values(result_shp,IOU_mapped_polygons,IOU_threshold, False,save_FP_path)
    basic.outputlogMessage('save false positives to %s'%save_FP_path)


    # calculate IOU
    IOU_groud_truth = vector_features.calculate_IoU_scores(val_shp, result_shp)
    save_FN_path = io_function.get_name_by_adding_tail(result_shp,'FN')
    # set False, remove greater than the threshold one
    remove_polygons_based_values(val_shp,IOU_groud_truth,IOU_threshold, False,save_FN_path)
    basic.outputlogMessage('save false negatives to %s'%save_FN_path)


def main(options, args):
    input = args[0]
    val_path = options.validation_shp

    para_file = options.para_file
    if val_path is None:
        # read validation shp from the parameter file
        multi_val_files = parameters.get_string_parameters_None_if_absence(para_file, 'validation_shape_list')
        if multi_val_files is None:
            val_path = parameters.get_validation_shape()
        else:
            cwd_path = os.getcwd()
            if os.path.isfile(multi_val_files) is False:
                multi_val_files = os.path.join(os.path.dirname(os.path.dirname(cwd_path)), multi_val_files)
            with open(multi_val_files, 'r') as f_obj:
                lines = f_obj.readlines()
                lines = [item.strip() for item in lines]

            folder = os.path.basename(cwd_path)
            import re
            I_idx_str = re.findall(r'I\d+', folder)
            if len(I_idx_str) == 1:
                index = int(I_idx_str[0][1:])
            else:
                # try to find the image idx from file name
                file_name = os.path.basename(input)
                I_idx_str = re.findall(r'I\d+', file_name)
                if len(I_idx_str) == 1:
                    index = int(I_idx_str[0][1:])
                else:
                    raise ValueError('Cannot find the I* which represents the image index')

            val_path = lines[index]
            # try to change the home folder path if the file does not exist
            val_path = io_function.get_file_path_new_home_folder(val_path)

    if os.path.isfile(val_path) is False:
        raise IOError('validation polygon (%s) not exist, cannot save FP and FN polygons'%val_path)

    save_false_positve_and_false_negative(input,val_path,para_file)


if __name__=='__main__':
    usage = "usage: %prog [options] input_path "
    parser = OptionParser(usage=usage, version="1.0 2020-9-03")
    parser.description = 'Introduction: saving the false positive and fase negatives in the mapped polygons according to their IOU values '
    parser.add_option("-p", "--para",
                      action="store", dest="para_file",
                      help="the parameters file")

    parser.add_option("-v", "--validation_shp",
                      action="store", dest="validation_shp",
                      help="the validation shape file  (ground truth)")

    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
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
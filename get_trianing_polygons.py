#!/usr/bin/env python
# Filename: get_trianing_polygons 
"""
introduction: randomly select training polygons from positive and negative ground truth polygons

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 19 October, 2018
"""

import os, sys

from optparse import OptionParser
import parameters

import basic_src.basic as basic
import basic_src.io_function as io_function
from vector_features import shape_opeation


def get_training_polygons(gt_shp,out_shp, per):
    """
    randomly select training polygons from positive and negative ground truth polygons
    Args:
        gt_shp: the shape file of ground truth polygons
        out_shp: save path
        per: percentage for selecting.

    Returns: True if successfully, False othersize

    """
    if io_function.is_file_exist(gt_shp) is False:
        return False

    operation_obj = shape_opeation()

    if operation_obj.get_portition_of_polygons(gt_shp,out_shp,per,"class_int"):
        operation_obj = None
        return True
    else:
        operation_obj = None
        return False

def get_k_fold_training_polygons(gt_shp,out_shp, k):
    """
    split polygons to k-fold,
    Each fold is then used once as a validation while the k - 1 remaining folds form the training set.
    similar to sklearn.model_selection.KFold, but apply to polygons in a shapefile
    Args:
        gt_shp: input
        out_shp:  output, will output k shapefiles in the same directory with the basename of "out_shp"
        k: k value

    Returns: True if successful, False Otherwise

    """
    if io_function.is_file_exist(gt_shp) is False:
        return False

    operation_obj = shape_opeation()

    return operation_obj.get_k_fold_of_polygons(gt_shp,out_shp,k,"class_int",shuffle = True)
    # return operation_obj.get_k_fold_of_polygons(gt_shp, out_shp, k, sep_field_name = None, shuffle=True)



def main(options, args):

    shp_GT = args[0]
    out_shp = args[1]
    percentage = options.percentage
    k_fold = options.k_fold
    # print(k_fold,percentage)

    if k_fold > 1:
        # get k shapefiles for k-fold cross validation
        get_k_fold_training_polygons(shp_GT,out_shp,k_fold)

    else:
        # get a shapefiles by randomly selecting a portion of polygons
        if get_training_polygons(shp_GT,out_shp,percentage) is False:
            sys.exit(1)




if __name__=='__main__':
    usage = "usage: %prog [options] input_path output_file"
    parser = OptionParser(usage=usage, version="1.0 2018-10-19")
    parser.description = 'Introduction: randomly select training polygons '

    # parser.add_option("-p", "--para",
    #                   action="store", dest="para_file",
    #                   help="the parameters file")

    parser.add_option("-s", "--selected_per",
                      action="store", dest="percentage",type=float,default=0.7,
                      help="the percentage of selecting")

    parser.add_option("-k", "--k_fold",
                      action="store", dest="k_fold",type=int,default=0,
                      help="K value for k-fold cross validation, should be > 1, then selected_per would be ignored,"
                           "if k=0 or 1, then k_fold would be ignore")


    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 2:
        parser.print_help()
        sys.exit(2)

    ## set parameters files
    # if options.para_file is None:
    #     print('error, no parameters file')
    #     parser.print_help()
    #     sys.exit(2)
    # else:
    #     parameters.set_saved_parafile_path(options.para_file)

    # test
    # ouput_merged = args[0]
    # dem_file = parameters.get_dem_file()
    # slope_file = parameters.get_slope_file()
    # calculate_gully_topography(ouput_merged,dem_file,slope_file)

    main(options, args)
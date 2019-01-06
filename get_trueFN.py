#!/usr/bin/env python
# Filename: plot_accuracies
"""
introduction: the the number of true false negatives:
means that the ground truths don’t have corresponding mapped polygons even the IOU_thr = 0.01

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 5 Jan, 2019
"""

import os, sys
from optparse import OptionParser

import numpy as np

# import vector_features
import vector_features
import parameters
import basic_src.io_function as io_function
import basic_src.basic as basic


def get_iou_scores(result_shp, ground_truth_shp):
    """
    get IoU scores of all the polygons in result_shp
    Args:
        result_shp: the path of result file
        ground_truth_shp: the path of ground truth file

    Returns: IoU values

    """
    IoUs = vector_features.calculate_IoU_scores(result_shp, ground_truth_shp)
    return IoUs



def calculate_precision_recall_iou(IoU_prediction,IoU_ground_truth,iou_threshold):
    """
    calculate precision, recall based on IoU values
    Args:
        IoU_prediction: IoU of each mapped polygons, should be 1d numpy array
        IoU_ground_truth: IoU of each ground truth polygons: for count false negatives, should be 1d numpy array
        iou_threshold: IoU threshold

    Returns: precision, recall, f1 score

    """
    true_pos_count = 0
    false_pos_count = 0

    # calculate precision, recall, F1 score
    for iou in IoU_prediction:
        if iou > iou_threshold:
            true_pos_count  +=  1
        else:
            false_pos_count += 1

    # false_neg_count = val_polygon_count - true_pos_count
    false_neg_count = len(IoU_ground_truth[np.where(IoU_ground_truth < iou_threshold)])
    basic.outputlogMessage('the number of true negatives: %d'%false_neg_count)

    if false_neg_count < 0:
        basic.outputlogMessage('warning, false negative count is smaller than 0, recall can not be trusted')

    basic.outputlogMessage('TP, FP, FN: %d, %d, %d'%(true_pos_count,false_pos_count,false_neg_count))

    precision = float(true_pos_count) / (float(true_pos_count) + float(false_pos_count))
    recall = float(true_pos_count) / (float(true_pos_count) + float(false_neg_count))
    if (true_pos_count > 0):
        F1score = 2.0 * precision * recall / (precision + recall)
    else:
        F1score = 0

    return precision, recall, F1score


def main(options, args):

    shape_file = args[0]
    if io_function.is_file_exist(shape_file) is False:
        return False

    # get ground truth polygons
    val_path = parameters.get_validation_shape()    # ground truth


    input_shp = shape_file
    groud_truth_shp = val_path
    basic.outputlogMessage('result shape: %s'%input_shp)
    basic.outputlogMessage('ground truth shape: %s'%groud_truth_shp)
    # calculate the IoU of each predicted polygons
    iou_pre = np.array(get_iou_scores(input_shp, groud_truth_shp))

    # calculate the IoU of each ground truth, for false negative
    iou_GT = np.array(get_iou_scores(groud_truth_shp, input_shp))

    iou_thr = 0.01
    precision, recall, f1score = calculate_precision_recall_iou(iou_pre, iou_GT, iou_thr)
    basic.outputlogMessage("precision, recall, f1score: %f,%f,%f"%(precision, recall, f1score))



if __name__ == '__main__':

    usage = "usage: %prog [options] shapefile"
    parser = OptionParser(usage=usage, version="1.0 2019-1-5")
    parser.description = 'Introduction: the the number of true false negatives:  '

    parser.add_option("-p", "--para",
                      action="store", dest="para_file",default='para.ini',
                      help="the parameters file")


    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)
    # set parameters files, mandatory for the path of ground truth polygons
    if options.para_file is None:
        print('error, no parameters file')
        parser.print_help()
        sys.exit(2)
    else:
        parameters.set_saved_parafile_path(options.para_file)

    main(options, args)


    pass


#!/usr/bin/env python
# Filename: plot_accuracies
"""
introduction: plot accuracies of the results, including Receiver Operating Characteristic (ROC),
            and Precision-Recall

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 31 Dec, 2018
"""

import os, sys
from optparse import OptionParser


import matplotlib.pyplot as plt
import numpy as np

# import vector_features
import vector_features
from vector_features import shape_opeation
import parameters
import basic_src.io_function as io_function
import basic_src.basic as basic

from sklearn.metrics import f1_score
from sklearn.metrics import precision_recall_fscore_support


# plt.rc('xtick',labelsize=20)
# plt.rc('ytick',labelsize=20)

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

def get_y_true_prediction(input_shp,groud_truth_shp,iou_threshold):
    """
    get ground truth and prediction array of polygons based on IoU values
    Args:
        input_shp: shape file of mapped polygons
        groud_truth_shp: shape file of ground truth polygons
        iou_threshold: iou threshold

    Returns: y_true,y_prediction ( numpy array)

    """

    # calculate the IoU of each predicted polygons
    iou_pre = np.array(get_iou_scores(input_shp, groud_truth_shp))

    # calculate the IoU of each ground truth, for false negative
    iou_GT = np.array(get_iou_scores(groud_truth_shp, input_shp))

    count_pre = len(iou_pre)
    y_pred = np.ones(count_pre)  # all the predicted output are considered as targets (1)

    # set true positive and false positve
    y_true = np.zeros(count_pre)
    y_true[np.where(iou_pre > iou_threshold)] = 1

    # modify y_true based on iou_GT for false negative
    count_false_neg = len(iou_GT[np.where(iou_GT < iou_threshold)])
    print(count_false_neg)
    # idx = 0
    # while (count_false_neg>0):
    #     print(idx)
    #     if y_true[idx]==0 and y_pred[idx] == 1: # all y_pred are 1
    #         y_true[idx] = 1
    #         y_pred[idx] = 0
    #         count_false_neg -= 1
    #     idx += 1
    # add false negatives
    y_true = np.append(y_true, np.ones(count_false_neg))
    y_pred = np.append(y_pred, np.zeros(count_false_neg))

    # tp = np.where(y_true==1 and y_pred==1)
    tp = 0
    fp = 0
    fn = 0
    for y_t, y_p in zip(y_true, y_pred):
        if y_p == 1 and y_t == 1:
            tp += 1
        elif y_p == 1 and y_t == 0:
            fp += 1
        elif y_p == 0 and y_t == 1:
            fn += 1
        else:
            pass
    print('tp=%d, fp=%d, fn=%d' % (tp, fp, fn))

    return y_true,y_pred


def get_y_true_and_scores(input_shp,groud_truth_shp):
    """
    get ground truth and the scores (IoU values) array of polygons
    Args:
        input_shp: shape file of mapped polygons
        groud_truth_shp: shape file of ground truth polygons

    Returns: y_true,y_scores ( numpy array)

    """

    # calculate the IoU of each predicted polygons
    iou_pre = np.array(get_iou_scores(input_shp, groud_truth_shp))

    # it seems unable to get it  1 Jan 2019

    # return y_true,y_pred


def calculate_f1_score(input_shp,groud_truth_shp,threshold):

    y_true, y_pred = get_y_true_prediction(input_shp,groud_truth_shp,threshold)
    # score = f1_score(y_true, y_pred) #, default average='binary'
    p_r_f1 =precision_recall_fscore_support(y_true, y_pred,average='binary')
    print(p_r_f1)

    return True

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

    if false_neg_count < 0:
        basic.outputlogMessage('warning, false negative count is smaller than 0, recall can not be trusted')

    precision = float(true_pos_count) / (float(true_pos_count) + float(false_pos_count))
    recall = float(true_pos_count) / (float(true_pos_count) + float(false_neg_count))
    if (true_pos_count > 0):
        F1score = 2.0 * precision * recall / (precision + recall)
    else:
        F1score = 0

    return precision, recall, F1score

def calculate_average_precision(precision_list,recall_list):
    """
    compute average_precision
    Args:
        precision_list: list of precision
        recall_list:    list of recall

    Returns:

    """

    count = len(precision_list)
    if len(recall_list) != count:
        raise ValueError("the number in precision_list and recall_list is inconsistent")

    ap = 0
    for idx in range(1,count):
        ap += precision_list[idx]*(recall_list[idx] - recall_list[idx-1])

    return ap


def precision_recall_curve_iou(input_shp,groud_truth_shp):
    """
    instead of using precision_recall_curve in sklearn.metrics, here we calculate the precision recall based on IoU
    Args:
        input_shp: shape file of mapped polygons
        groud_truth_shp:shape file of ground truth polygons

    Returns: precision, recall, threshold

    """

    # calculate the IoU of each predicted polygons
    iou_pre = np.array(get_iou_scores(input_shp, groud_truth_shp))

    # calculate the IoU of each ground truth, for false negative
    iou_GT = np.array(get_iou_scores(groud_truth_shp, input_shp))

    precision_list = []
    recall_list = []
    iou_thr_list = []
    f1score_list = []
    # for iou_thr in np.arange(0, 1, 0.05):
    for iou_thr in np.arange(1, -0.01, -0.05):
        precision, recall, f1score = calculate_precision_recall_iou(iou_pre, iou_GT, iou_thr)
        print(precision, recall, f1score)
        precision_list.append(precision)
        recall_list.append(recall)
        f1score_list.append(f1score)
        iou_thr_list.append(iou_thr)

    return precision_list, recall_list, iou_thr_list


def plot_precision_recall_curve(input_shp,groud_truth_shp,save_path):
    # from sklearn.metrics import precision_recall_curve

    from sklearn.utils.fixes import signature

    precision, recall, _ = precision_recall_curve_iou(input_shp,groud_truth_shp)

    average_precision = calculate_average_precision(precision,recall)

    # In matplotlib < 1.5, plt.fill_between does not have a 'step' argument
    step_kwargs = ({'step': 'post'}
                   if 'step' in signature(plt.fill_between).parameters
                   else {})
    plt.step(recall, precision, color='b', alpha=0.2,
             where='post')
    plt.fill_between(recall, precision, alpha=0.2, color='b', **step_kwargs)

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.title('2-class Precision-Recall curve: AP={0:0.2f}'.format(
        average_precision))

    # plt.show()
    plt.savefig(save_path,dpi=300)
    basic.outputlogMessage("Output figures to %s" % os.path.abspath(save_path))


def main(options, args):

    shape_file = args[0]
    if io_function.is_file_exist(shape_file) is False:
        return False

    # get ground truth polygons
    val_path = parameters.get_validation_shape()    # ground truth

    # calculate f1 score
    # calculate_f1_score(shape_file,val_path,0.5)

    # precision_recall_curve_iou(shape_file, val_path)
    plot_precision_recall_curve(shape_file, val_path,'P_R.jpg')





if __name__ == '__main__':

    usage = "usage: %prog [options] shapefile"
    parser = OptionParser(usage=usage, version="1.0 2017-10-28")
    parser.description = 'Introduction: plot accuracies of the results  '

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


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

    # val_polygon_count = len(IoU_ground_truth)
    # false_neg_count = val_polygon_count - true_pos_count

    # use the following method, because in beiluhe case, a mapped polygon can cover two or more thaw slumps
    if iou_threshold <= 0:
        false_neg_count = len(IoU_ground_truth[np.where(IoU_ground_truth ==0 )])
    else:
        false_neg_count = len(IoU_ground_truth[np.where(IoU_ground_truth < iou_threshold)])

    if false_neg_count < 0:
        basic.outputlogMessage('warning, false negative count is smaller than 0, recall can not be trusted')

    precision = float(true_pos_count) / (float(true_pos_count) + float(false_pos_count))
    recall = float(true_pos_count) / (float(true_pos_count) + float(false_neg_count))
    if (true_pos_count > 0):
        F1score = 2.0 * precision * recall / (precision + recall)
    else:
        F1score = 0
    basic.outputlogMessage("iou_thr: %.3f,TP:%3d, FP:%3d, FN:%3d, TP+FP:%3d, TP+FN:%3d"%(iou_threshold,true_pos_count,false_pos_count,false_neg_count,
                                                          true_pos_count+false_pos_count,true_pos_count+false_neg_count))
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
        ap += precision_list[idx]*(recall_list[idx] - recall_list[idx-1]) #abs

    return ap


def precision_recall_curve_iou(input_shp,groud_truth_shp):
    """
    instead of using precision_recall_curve in sklearn.metrics, here we calculate the precision recall based on IoU
    Args:
        input_shp: shape file of mapped polygons
        groud_truth_shp:shape file of ground truth polygons

    Returns: precision, recall, threshold

    """
    basic.outputlogMessage('calculate precision recall curve for %s'%input_shp)

    # calculate the IoU of each predicted polygons
    iou_pre = np.array(get_iou_scores(input_shp, groud_truth_shp))

    # calculate the IoU of each ground truth, for false negative
    iou_GT = np.array(get_iou_scores(groud_truth_shp, input_shp))

    precision_list = []
    recall_list = []
    iou_thr_list = []
    f1score_list = []
    # for iou_thr in np.arange(-0.01, 1.01, 0.05):
    for iou_thr in np.arange(1, -0.01, -0.04): #-0.05
        # abs(iou_thr) >=0, it is strange (0 > -0.000 return true), Jan 16 2019. hlc
        # but it turns our that precision cannot be 1, so just keep it.
        # iou_thr = abs(iou_thr)
        if iou_thr < 0:
            iou_thr = 0
        precision, recall, f1score = calculate_precision_recall_iou(iou_pre, iou_GT, iou_thr) #abs(iou_thr)
        basic.outputlogMessage("iou_thr: %.3f, precision: %.4f, recall: %.4f, f1score: %.4f"%(iou_thr,precision, recall, f1score))
        precision_list.append(precision)
        recall_list.append(recall)
        f1score_list.append(f1score)
        iou_thr_list.append(iou_thr)

    return precision_list, recall_list, iou_thr_list


def plot_precision_recall_curve(input_shp,groud_truth_shp,save_path):
    # from sklearn.metrics import precision_recall_curve

    try:
        from sklearn.utils.fixes import signature
    except ImportError:
        from funcsigs import signature

    precision, recall, _ = precision_recall_curve_iou(input_shp,groud_truth_shp)

    average_precision = calculate_average_precision(precision,recall)

    # In matplotlib < 1.5, plt.fill_between does not have a 'step' argument
    step_pos = 'mid' # post
    step_kwargs = ({'step': step_pos}
                   if 'step' in signature(plt.fill_between).parameters
                   else {})
    plt.step(recall, precision, color='b', alpha=0.2,
             where=step_pos)
    plt.plot(recall, precision, 'r--')
    plt.fill_between(recall, precision, alpha=0.2, color='b', **step_kwargs)

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([-0.01, 1.05])
    plt.xlim([-0.01, 1.01])
    plt.title('2-class Precision-Recall curve: AP={0:0.2f}'.format(
        average_precision))

    # save average_precision to txt file
    txt_path = os.path.splitext(save_path)[0]+'_ap.txt'
    with open(txt_path,'w') as f_obj:
        f_obj.writelines('shape_file    average_precision\n')
        f_obj.writelines('%s %.4lf\n' % (input_shp, average_precision))

    # plt.show()
    plt.savefig(save_path,dpi=300)
    basic.outputlogMessage("Output figures to %s" % os.path.abspath(save_path))

def plot_precision_recall_curve_multi(input_shp_list,groud_truth_shp,save_path,legend_loc='best'):
    """
    plot precision_recall of multi shapefiles to a figure
    Args:
        input_shp_list: a list of shapefiles
        groud_truth_shp: the ground truth file
        save_path: output figure path

    Returns:

    """

    precision_list = []
    recall_list = []
    average_precision_list = []
    line_labels = []
    for idx,input_shp in enumerate(input_shp_list):
        precision, recall, _ = precision_recall_curve_iou(input_shp, groud_truth_shp)
        precision_list.append(precision)
        recall_list.append(recall)

        average_precision = calculate_average_precision(precision, recall)
        average_precision_list.append(average_precision)

        file_name = os.path.splitext(os.path.basename(input_shp))[0]
        if 'fold' in file_name:     # k-fold cross-validation
            tmp = file_name.split('_')
            label = '_'.join(tmp[-3:])
        elif 'imgAug' in file_name: # image augmentation test
            tmp = file_name.split('_')
            label = tmp[-1]
        else:
            label = str(idx)

        line_labels.append('%s: AP=%.2f'%(label,average_precision))

    # save average_precision to txt file
    txt_path = os.path.splitext(save_path)[0]+'_ap.txt'
    with open(txt_path,'w') as f_obj:
        f_obj.writelines('shape_file    average_precision\n')
        for shp_file,average_pre in zip(input_shp_list,average_precision_list):
            f_obj.writelines('%s %.4lf\n'%(shp_file,average_pre))

    # matplotlib build-in color
    # b: blue
    # g: green
    # r: red
    # c: cyan
    # m: magenta
    # y: yellow
    # k: black
    # w: white

    line_color = ['b', 'g', 'r', 'c', 'y', 'k','m'] #
    linestyle = ['-','--','-.',":",'+-','x-']
    # linestyle = [ '+','x' ,'*','s', 'h',  'd', 'p', 'H', 'D'] #,
    color_used_count = len(line_color)
    line_used_count = len(linestyle)

    for x in range(0,len(input_shp_list)):
        recall = recall_list[x]
        precision = precision_list[x]

        outlook = line_color[x % color_used_count] + linestyle[x // color_used_count]
        step_pos = 'mid'
        plt.step(recall, precision, outlook, where=step_pos,label=line_labels[x])
        # plt.plot(recall, precision, 'r--')

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([-0.01, 1.05])
    plt.xlim([-0.01, 1.01])
    plt.title('Precision-Recall curve')
    print('********legend_loc*************', legend_loc)
    if legend_loc=='best':
        plt.legend(loc='best', bbox_to_anchor=(1, 0.5), title="Average Precision", fontsize=9)
    else:
        plt.legend(loc=legend_loc, title="Average Precision", fontsize=9)

    # plt.show()
    plt.savefig(save_path, dpi=300)
    basic.outputlogMessage("Output figures to %s" % os.path.abspath(save_path))

    return True

def main(options, args):

    shape_file = args[0]
    if io_function.is_file_exist(shape_file) is False:
        return False

    out_fig_path = options.output

    # get ground truth polygons
    val_path = parameters.get_validation_shape()    # ground truth
    basic.outputlogMessage('the ground truth polygons are in %s'%val_path)

    # calculate f1 score
    # calculate_f1_score(shape_file,val_path,0.5)

    # precision_recall_curve_iou(shape_file, val_path)
    if len(args) == 1:
        plot_precision_recall_curve(shape_file, val_path,out_fig_path)
    else:
        plot_precision_recall_curve_multi(args, val_path, out_fig_path)



if __name__ == '__main__':

    usage = "usage: %prog [options] shapefile or shapefiles"
    parser = OptionParser(usage=usage, version="1.0 2017-10-28")
    parser.description = 'Introduction: plot accuracies of the results  '

    parser.add_option("-p", "--para",
                      action="store", dest="para_file",default='para.ini',
                      help="the parameters file")
    parser.add_option("-o", "--output",
                      action="store", dest="output",default='P_R.jpg',
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

    basic.setlogfile('accuracies_log.txt')

    main(options, args)


    pass


#!/usr/bin/env python
# Filename: post_process 
"""
introduction:

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 27 March, 2017
"""
from optparse import OptionParser
import basic_src.basic as basic
import basic_src.io_function as io_function
import os,sys

# import  parameters
import vector_features
from vector_features import shape_opeation
import parameters


def remove_nonclass_polygon(input_shp,output_shp, field_name='svmclass'):
    """
    remove polygon which is not belong to target
    :param input_shp: input shape file
    :param output_shp: output shape file
    :param field_name: the field name of specific field containing class information in the shape file
    :return: True if successful, False Otherwise
    """
    operation_obj = shape_opeation()
    if operation_obj.remove_nonclass_polygon(input_shp, output_shp, field_name):
        operation_obj = None
        return True
    else:
        operation_obj = None
        return False

def merge_polygons_in_gully(input_shp, output_shp):
    """
    merge polygons in one gully. supposed that the polygons touch each other are belong to the same gully
    :param input_shp: input shapfe file
    :param output_shp: output shape file contains the merged polygons
    :return: True if successful, False Otherwise
    """
    return vector_features.merge_touched_polygons_in_shapefile(input_shp,output_shp )

def calculate_gully_information(gullies_shp):
    """
    get Oriented minimum bounding box for the gully polygon shapefile,
    and update the shape information based on oriented minimum bounding box to
        the gullies_shp
    :param gullies_shp: input shapefile contains the gully polygons
    :return: True if successful, False Otherwise
    """
    operation_obj = shape_opeation()
    output_shapeinfo = io_function.get_name_by_adding_tail(gullies_shp, 'shapeInfo')
    if os.path.isfile(output_shapeinfo) is False:
        operation_obj.get_polygon_shape_info(gullies_shp, output_shapeinfo)
    else:
        basic.outputlogMessage('warning, %s already exist, skip calculate shape feature' % output_shapeinfo)
    # put all feature to one shapefile
    # parameter 3 the same as parameter 1 to overwrite the input file

    # note: the area in here, is the area of the oriented minimum bounding box, not the area of polygon
    operation_obj.add_fields_shape(gullies_shp, output_shapeinfo, gullies_shp)

    # add width/height (suppose height greater than width)
    width_height_list = operation_obj.get_shape_records_value(gullies_shp,attributes=['WIDTH','HEIGHT'])
    ratio = []
    for width_height in width_height_list:
        if width_height[0] > width_height[1]:
            r_value = width_height[1] / width_height[0]
        else:
            r_value = width_height[0] / width_height[1]
        ratio.append(r_value)
    operation_obj.add_one_field_records_to_shapefile(gullies_shp,ratio,'ratio_w_h')

    # add perimeter/area
    perimeter_area_list = operation_obj.get_shape_records_value(gullies_shp, attributes=['INperimete','INarea'])
    if perimeter_area_list is False:
        return False
    ratio_p_a = []
    for perimeter_area in perimeter_area_list:
        r_value = (perimeter_area[0])**2 / perimeter_area[1];
        ratio_p_a.append(r_value)
    operation_obj.add_one_field_records_to_shapefile(gullies_shp, ratio_p_a, 'ratio_p_a')

    return True

def remove_small_round_polygons(input_shp,output_shp,area_thr,ratio_thr):
    """
    remove the polygons that is not gully, that is the polygon is too small or not narrow.
    # too small or not narrow
    :param input_shp: input shape file
    :param output_shp:  output  shape file
    :return: True if successful, False otherwise
    """

    #remove the too small polygon
    operation_obj = shape_opeation()
    output_rm_small = io_function.get_name_by_adding_tail(input_shp,'rmSmall')
    # area_thr = parameters.get_minimum_gully_area()
    if operation_obj.remove_shape_baseon_field_value(input_shp,output_rm_small,'INarea',area_thr,smaller=True) is False:
        return False

    # remove the not narrow polygon
    # it seems that this can not represent how narrow the polygon is, because they are irregular polygons
    # whatever, it can remove some flat, and not long polygons. if you want to omit this, just set the maximum_ratio_width_height = 1

    output_rm_Rwh=io_function.get_name_by_adding_tail(input_shp,'rmRwh')
    ratio_thr = parameters.get_maximum_ratio_width_height()
    if operation_obj.remove_shape_baseon_field_value(output_rm_small, output_rm_Rwh, 'ratio_w_h', ratio_thr, smaller=False) is False:
        return False

    #  remove the not narrow polygon based on ratio_p_a
    ratio_thr = parameters.get_minimum_ratio_perimeter_area()
    if operation_obj.remove_shape_baseon_field_value(output_rm_Rwh, output_shp, 'ratio_p_a', ratio_thr, smaller=True) is False:
        return False

    return True

def evaluation_result(result_shp,val_shp):
    """
    evaluate the result based on IoU
    :param result_shp: result shape file contains detected polygons
    :param val_shp: shape file contains validation polygons
    :return: True is successful, False otherwise
    """
    basic.outputlogMessage("evaluation result")
    IoUs = vector_features.calculate_IoU_scores(result_shp,val_shp)
    if IoUs is False:
        return False

    #save IoU to result shapefile
    operation_obj = shape_opeation()
    operation_obj.add_one_field_records_to_shapefile(result_shp, IoUs, 'IoU')

    iou_threshold = parameters.get_IOU_threshold()
    true_pos_count = 0
    false_pos_count = 0
    val_polygon_count = operation_obj.get_shapes_count(val_shp)
    # calculate precision, recall, F1 score
    for iou in IoUs:
        if iou > iou_threshold:
            true_pos_count  +=  1
        else:
            false_pos_count += 1

    false_neg_count = val_polygon_count - true_pos_count
    if false_neg_count < 0:
        basic.outputlogMessage('warning, false negative count is smaller than 0, recall can not be trusted')

    precision = float(true_pos_count) / (float(true_pos_count) + float(false_pos_count))
    recall = float(true_pos_count) / (float(true_pos_count) + float(false_neg_count))
    if (true_pos_count > 0):
        F1score = 2.0 * precision * recall / (precision + recall)
    else:
        F1score = 0

    #output evaluation reslult
    evaluation_txt = "evaluation_report.txt"
    f_obj = open(evaluation_txt,'w')
    f_obj.writelines('true_pos_count: %d\n'%true_pos_count)
    f_obj.writelines('false_pos_count: %d\n'% false_pos_count)
    f_obj.writelines('false_neg_count: %d\n'%false_neg_count)
    f_obj.writelines('precision: %.6f\n'%precision)
    f_obj.writelines('recall: %.6f\n'%recall)
    f_obj.writelines('F1score: %.6f\n'%F1score)
    f_obj.close()


    pass


def main(options, args):
    input = args[0]
    output = args[1]

    if io_function.is_file_exist(input) is False:
        return False

    ## remove non-gully polygons
    # output_rm_nonclass = io_function.get_name_by_adding_tail(input, 'rm_nonclass')
    # if remove_nonclass_polygon(input,output_rm_nonclass,field_name='svmclass') is False:
    #     return False

    # merge the touched polygons
    ouput_merged = io_function.get_name_by_adding_tail(input,'merged')
    if merge_polygons_in_gully(input,ouput_merged) is False:
        return False

    # calculate the polygon information
    if calculate_gully_information(ouput_merged) is False:
        return False

    # remove small and not narrow polygons
    if options.min_area is None:
        basic.outputlogMessage('minimum area is required for remove polygons')
        return False
    area_thr = options.min_area

    if options.min_ratio is None:
        basic.outputlogMessage('minimum ratio of perimeter/area is required for remove polygons')
        return False
    ratio_thr = options.min_ratio

    remove_small_round_polygons(ouput_merged,output,area_thr,ratio_thr)

    # evaluation result
    val_path = parameters.get_validation_shape()
    evaluation_result(output,val_path)

    pass


if __name__=='__main__':
    usage = "usage: %prog [options] input_path output_file"
    parser = OptionParser(usage=usage, version="1.0 2017-7-24")
    parser.description = 'Introduction: Post process of Polygon shape file, including  ' \
                         'statistic polygon information, remove small area polygon,' \
                         'remove  '
    parser.add_option("-p", "--para",
                      action="store", dest="para_file",
                      help="the parameters file")

    parser.add_option("-a", "--min_area",
                      action="store", dest="min_area",type=float,
                      help="the minimum for each polygon")
    parser.add_option("-r", "--min_ratio",
                      action="store", dest="min_ratio",type=float,
                      help="the minimum ratio (perimeter*perimeter / area) for each polygon (thin and long polygon has larger ratio)")

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

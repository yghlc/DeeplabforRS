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
import math

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

def cal_add_area_length_of_polygon(input_shp):
    """
    calculate the area, perimeter of polygons, save to the original file
    :param input_shp: input shapfe file
    :return: True if successful, False Otherwise
    """
    return vector_features.cal_area_length_of_polygon(input_shp )

def calculate_gully_topography(polygons_shp,dem_file,slope_file,aspect_file=None):
    """
    calculate the topography information such elevation and slope of each polygon
    Args:
        polygons_shp: input shapfe file
        dem_file: DEM raster file, should have the same projection of shapefile
        slope_file: slope raster file (can be drived from dem file by using QGIS or ArcGIS)
        aspect_file: aspect raster file (can be drived from dem file by using QGIS or ArcGIS)

    Returns: True if successful, False Otherwise
    """
    if io_function.is_file_exist(polygons_shp) is False:
        return False
    operation_obj = shape_opeation()

    ## calculate the topography information from the buffer area

    # the para file was set in parameters.set_saved_parafile_path(options.para_file)
    b_use_buffer_area = parameters.get_bool_parameters('','b_topo_use_buffer_area', None)

    if b_use_buffer_area is True:

        b_buffer_size = 5  # meters (the same as the shape file)

        basic.outputlogMessage("info: calculate the topography information from the buffer area")
        buffer_polygon_shp = io_function.get_name_by_adding_tail(polygons_shp, 'buffer')
        # if os.path.isfile(buffer_polygon_shp) is False:
        if vector_features.get_buffer_polygons(polygons_shp,buffer_polygon_shp,b_buffer_size) is False:
            basic.outputlogMessage("error, failed in producing the buffer_polygon_shp")
            return False
        # else:
        #     basic.outputlogMessage("warning, buffer_polygon_shp already exist, skip producing it")
        # replace the polygon shape file
        polygons_shp_backup = polygons_shp
        polygons_shp = buffer_polygon_shp
    else:
        basic.outputlogMessage("info: calculate the topography information from the inside of each polygon")



    # all_touched: bool, optional
    #     Whether to include every raster cell touched by a geometry, or only
    #     those having a center point within the polygon.
    #     defaults to `False`
    #   Since the dem usually is coarser, so we set all_touched = True
    all_touched = True

    # #DEM
    if os.path.isfile(dem_file):
        stats_list = ['min', 'max','mean', 'std']            #['min', 'max', 'mean', 'count','median','std']
        if operation_obj.add_fields_from_raster(polygons_shp, dem_file, "dem", band=1,stats_list=stats_list,all_touched=all_touched) is False:
            return False
    else:
        basic.outputlogMessage("warning, DEM file not exist, skip the calculation of DEM information")

    # #slope
    if os.path.isfile(slope_file):
        stats_list = ['min', 'max','mean', 'std']
        if operation_obj.add_fields_from_raster(polygons_shp, slope_file, "slo", band=1,stats_list=stats_list,all_touched=all_touched) is False:
            return False
    else:
        basic.outputlogMessage("warning, slope file not exist, skip the calculation of slope information")

    # #aspect
    if aspect_file is not None and os.path.isfile(aspect_file):
        if io_function.is_file_exist(aspect_file) is False:
            return False
        stats_list = ['min', 'max','mean', 'std']
        if operation_obj.add_fields_from_raster(polygons_shp, aspect_file, "asp", band=1,stats_list=stats_list,all_touched=all_touched) is False:
            return False
    else:
        basic.outputlogMessage('warning, aspect file not exist, ignore adding aspect information')

    # # hillshape

    # copy the topography information
    if b_use_buffer_area is True:
        operation_obj.add_fields_shape(polygons_shp_backup, buffer_polygon_shp, polygons_shp_backup)

    return True

def calculate_hydrology(polygons_shp,flow_accumulation):
    """
    calculate the hydrology information of each polygons
    Args:
        polygons_shp:  input shapfe file
        flow_accumulation: the file path of flow accumulation

    Returns: True if successful, False Otherwise

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

    stats_list = ['min', 'max', 'mean', 'std']  # ['min', 'max', 'mean', 'count','median','std']
    if operation_obj.add_fields_from_raster(polygons_shp, flow_accumulation, "F_acc", band=1, stats_list=stats_list,
                                                all_touched=all_touched) is False:
        return False


    pass

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
        # note: the area in here, is the area of the oriented minimum bounding box, not the area of polygon
        operation_obj.add_fields_shape(gullies_shp, output_shapeinfo, gullies_shp)
    else:
        basic.outputlogMessage('warning, %s already exist, skip calculate and add shape feature' % output_shapeinfo)
    # put all feature to one shapefile
    # parameter 3 the same as parameter 1 to overwrite the input file

    # add width/height (suppose height greater than width)
    width_height_list = operation_obj.get_shape_records_value(gullies_shp,attributes=['WIDTH','HEIGHT'])
    if width_height_list is not False:
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
    if perimeter_area_list is not False:
        ratio_p_a = []
        for perimeter_area in perimeter_area_list:
            r_value = (perimeter_area[0])**2 / perimeter_area[1]
            ratio_p_a.append(r_value)
        operation_obj.add_one_field_records_to_shapefile(gullies_shp, ratio_p_a, 'ratio_p_a')

    # add circularity (4*pi*area/perimeter**2) which is similar to ratio_p_a
    circularity = []
    for perimeter_area in perimeter_area_list:
        value = (4*math.pi*perimeter_area[1] / perimeter_area[0] ** 2)
        circularity.append(value)
    operation_obj.add_one_field_records_to_shapefile(gullies_shp, circularity, 'circularit')

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

    ##########################################################################################
    ## another method for calculating false_neg_count base on IoU value
    # calculate the IoU for validation polygons (ground truths)
    IoUs = vector_features.calculate_IoU_scores(val_shp, result_shp)
    if IoUs is False:
        return False

    # if the IoU of a validation polygon smaller than threshold, then it's false negative
    false_neg_count = 0
    idx_of_false_neg = []
    for idx,iou in enumerate(IoUs):
        if iou < iou_threshold:
            false_neg_count +=  1
            idx_of_false_neg.append(idx+1) # index start from 1

    precision = float(true_pos_count) / (float(true_pos_count) + float(false_pos_count))
    recall = float(true_pos_count) / (float(true_pos_count) + float(false_neg_count))
    if (true_pos_count > 0):
        F1score = 2.0 * precision * recall / (precision + recall)
    else:
        F1score = 0
    # output evaluation reslult
    evaluation_txt = "evaluation_report.txt"
    f_obj = open(evaluation_txt, 'a')  # add to "evaluation_report.txt"
    f_obj.writelines('\n\n** Count false negative by IoU**\n')
    f_obj.writelines('true_pos_count: %d\n' % true_pos_count)
    f_obj.writelines('false_pos_count: %d\n' % false_pos_count)
    f_obj.writelines('false_neg_count_byIoU: %d\n' % false_neg_count)
    f_obj.writelines('precision: %.6f\n' % precision)
    f_obj.writelines('recall: %.6f\n' % recall)
    f_obj.writelines('F1score: %.6f\n' % F1score)
    # output the index of false negative
    f_obj.writelines('\nindex (start from 1) of false negatives: %s\n' % ','.join([str(item) for item in idx_of_false_neg]))
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
    # ouput_merged = io_function.get_name_by_adding_tail(input,'merged')
    # if merge_polygons_in_gully(input,ouput_merged) is False:
    #     return False
    # ouput_merged = input

    # copy output
    if io_function.copy_shape_file(input, output) is False:
        raise IOError('copy shape file %s failed'%input)

    # calcuate area, perimeter of polygons
    if cal_add_area_length_of_polygon(output) is False:
        return False

    # calculate the polygon information
    if calculate_gully_information(output) is False:
        return False

    # # remove small and not narrow polygons
    # if options.min_area is None:
    #     basic.outputlogMessage('minimum area is required for remove polygons')
    #     return False
    # area_thr = options.min_area
    #
    # if options.min_ratio is None:
    #     basic.outputlogMessage('minimum ratio of perimeter/area is required for remove polygons')
    #     return False
    # ratio_thr = options.min_ratio

    # if remove_small_round_polygons(ouput_merged,output,area_thr,ratio_thr) is False:
    #     return False


    # add topography of each polygons
    dem_file = parameters.get_dem_file()
    slope_file = parameters.get_slope_file()
    aspect_file=parameters.get_aspect_file()
    if calculate_gully_topography(output,dem_file,slope_file,aspect_file) is False:
        basic.outputlogMessage('Warning: calculate information of topography failed')
        # return False   #  don't return


    # add hydrology information
    flow_accum = parameters.get_flow_accumulation()
    if os.path.isfile(flow_accum):
        if calculate_hydrology(output, flow_accum) is False:
            basic.outputlogMessage('Warning: calculate information of hydrology failed')
            # return False  #  don't return
    else:
        basic.outputlogMessage("warning, flow accumulation file not exist, skip the calculation of flow accumulation")

    # evaluation result
    val_path = parameters.get_validation_shape()
    if os.path.isfile(val_path):
        evaluation_result(output,val_path)
    else:
        basic.outputlogMessage("warning, validation polygon not exist, skip evaluation")

    pass


if __name__=='__main__':
    usage = "usage: %prog [options] input_path output_file"
    parser = OptionParser(usage=usage, version="1.0 2017-7-24")
    parser.description = 'Introduction: Post process of Polygon shape file, including  ' \
                         'statistic polygon information,' 
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

    # test
    # ouput_merged = args[0]
    # dem_file = parameters.get_dem_file()
    # slope_file = parameters.get_slope_file()
    # calculate_gully_topography(ouput_merged,dem_file,slope_file)



    main(options, args)

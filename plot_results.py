#!/usr/bin/env python
# Filename: plot_results 
"""
introduction: plot some statistic of the results

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 28 October, 2017
"""

import os,sys
from optparse import OptionParser

import parameters
import matplotlib.pyplot as plt

import plotly.plotly as py

# import vector_features
from vector_features import shape_opeation
import basic_src.io_function as io_function
import basic_src.basic as basic

def read_attribute(shapefile, field_name):
    """
    read one attribute of shapefile
    Args:
        shapefile: shapefile path
        field_name: name of the attribute

    Returns: a list contains the values of the field, False otherwise

    """
    operation_obj = shape_opeation()
    output_list = operation_obj.get_shape_records_value(shapefile, attributes=[field_name])
    if len(output_list) < 1:
        return False
    else:
        value_list = [item[0] for item in output_list]
        return value_list

def draw_one_attribute_histogram(shp_file,field_name,attribute, output):
    """
    draw the figure of one attribute's histograms
    Args:
        shp_file:  shape file path
        attribute_name: name of attribute
        output: output the figure

    Returns: True if successful, False otherwise

    """
    values = read_attribute(shp_file,field_name)

    plt.figure()  # create a new figure

    n, bins, patches = plt.hist(values, bins="auto", alpha=0.75,ec="black")  # ec means edge color

    plt.xlabel(attribute)
    plt.ylabel("Frequency")
    plt.title('Histogram of '+attribute)
    # plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    # plt.axis([40, 160, 0, 0.03])
    plt.grid(True)
    plt.savefig(output)
    basic.outputlogMessage("Output figures to %s"%os.path.abspath(output))
   # plt.show()



def main(options, args):

    shape_file = args[0]
    if io_function.is_file_exist(shape_file) is False:
        return False


    draw_one_attribute_histogram(shape_file, "INarea", "Area", "area.jpg")
    draw_one_attribute_histogram(shape_file, "INperimete", "Perimeter", "Perimeter.jpg")
    draw_one_attribute_histogram(shape_file, "ratio_w_h", "ratio of HEIGHT over WIDTH (W>H)", "ratio_w_h.jpg")
    draw_one_attribute_histogram(shape_file, "ratio_p_a", "ratio of perimeter^2 over area", "ratio_p_a.jpg")
    draw_one_attribute_histogram(shape_file, "circularit", "Circularity", "Circularity.jpg")

    # topography
    draw_one_attribute_histogram(shape_file, "dem_std", "standard variance of DEM", "dem_std.jpg")
    draw_one_attribute_histogram(shape_file, "dem_max", "maximum value of DEM", "dem_max.jpg")
    draw_one_attribute_histogram(shape_file, "dem_mean", "mean value of DEM", "dem_mean.jpg")
    draw_one_attribute_histogram(shape_file, "dem_min", "minimum value of DEM", "dem_min.jpg")

    draw_one_attribute_histogram(shape_file, "slo_std", "standard variance of Slope", "slo_std.jpg")
    draw_one_attribute_histogram(shape_file, "slo_max", "maximum value of Slope", "slo_max.jpg")
    draw_one_attribute_histogram(shape_file, "slo_mean", "mean value of Slope", "slo_mean.jpg")
    draw_one_attribute_histogram(shape_file, "slo_min", "minimum value of Slope", "slo_min.jpg")

    #hydrology
    draw_one_attribute_histogram(shape_file, "F_acc_std", "standard variance of Flow accumulation", "F_acc_std.jpg")
    draw_one_attribute_histogram(shape_file, "F_acc_max", "maximum value of Flow accumulation", "F_acc_max.jpg")
    draw_one_attribute_histogram(shape_file, "F_acc_mean", "mean value of Flow accumulation", "F_acc_mean.jpg")
    draw_one_attribute_histogram(shape_file, "F_acc_min", "minimum value of Flow accumulation", "F_acc_min.jpg")

    pass



if __name__ == '__main__':

    usage = "usage: %prog [options] shapefile"
    parser = OptionParser(usage=usage, version="1.0 2017-10-28")
    parser.description = 'Introduction: plot some statistic of the results  '
    parser.add_option("-p", "--para",
                      action="store", dest="para_file",
                      help="the parameters file")

    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)
    ## set parameters files
    # if options.para_file is None:
    #     print('error, no parameters file')
    #     parser.print_help()
    #     sys.exit(2)
    # else:
    #     parameters.set_saved_parafile_path(options.para_file)



    main(options, args)

    pass


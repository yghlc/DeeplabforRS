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

def draw_one_attribute_histogram(shp_file,attribute_name, output):
    """
    draw the figure of one attribute's histograms
    Args:
        shp_file:  shape file path
        attribute_name: name of attribute
        output: output the figure

    Returns: True if successful, False otherwise

    """
    values = read_attribute(shp_file,attribute_name)

    n, bins, patches = plt.hist(values, bins="auto", alpha=0.75)

    plt.xlabel(attribute_name)
    plt.ylabel("Frequency")
    plt.title('Histogram of '+attribute_name)
    # plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    # plt.axis([40, 160, 0, 0.03])
    # plt.grid(True)
    plt.show()



def main(options, args):

    shape_file = args[0]
    if io_function.is_file_exist(shape_file) is False:
        return False

    draw_one_attribute_histogram(shape_file,"ratio_p_a","ratio_p_a.jpg")

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


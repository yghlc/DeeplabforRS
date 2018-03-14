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
from mpl_toolkits.axes_grid.axislines import Subplot

import plotly.plotly as py

# import vector_features
from vector_features import shape_opeation
import basic_src.io_function as io_function
import basic_src.basic as basic

import json
import numpy as np

plt.rc('xtick',labelsize=20)
plt.rc('ytick',labelsize=20)



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

def draw_one_attribute_histogram(shp_file,field_name,attribute, output,color='grey',hatch=""):
    """
    draw the figure of one attribute's histograms
    Args:
        shp_file:  shape file path
        attribute_name: name of attribute
        output: output the figure

    Returns: True if successful, False otherwise

    """
    values = read_attribute(shp_file,field_name)

    fig_obj = plt.figure()  # create a new figure

    ax = Subplot(fig_obj, 111)
    fig_obj.add_subplot(ax)

    # n, bins, patches = plt.hist(values, bins="auto", alpha=0.75,ec="black")  # ec means edge color
    n, bins, patches = ax.hist(values, bins="auto", alpha=0.75, ec="black",linewidth='3',color=color,hatch=hatch)
    # print(n,bins,patches)
    # n_label = [str(i) for i in n]
    # plt.hist(values, bins="auto", alpha=0.75, ec="black",label=n_label)

    # plt.gcf().subplots_adjust(bottom=0.15)   # reserve space for label
    # plt.xlabel(attribute,fontsize=15)
    # # plt.ylabel("Frequency")
    # plt.ylabel("Number",fontsize=15)  #
    # # plt.title('Histogram of '+attribute)
    # # plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    # # plt.axis([40, 160, 0, 0.03])


    # hide the right and top boxed axis
    ax.axis["right"].set_visible(False)
    ax.axis["top"].set_visible(False)

    # plt.grid(True)
    plt.savefig(output)
    basic.outputlogMessage("Output figures to %s"%os.path.abspath(output))
    basic.outputlogMessage("ncount: " + str(n))
    basic.outputlogMessage("bins: "+ str(bins))
    # plt.show()

def get_hisogram_of_oneband_raster(image_path):
    if io_function.is_file_exist(image_path) is False:
        return False

    CommandString = 'gdalinfo -json -hist -mm ' + image_path
    imginfo = basic.exec_command_string_output_string(CommandString)
    if imginfo is False:
        return False
    imginfo_obj = json.loads(imginfo)

    try:
        bands_info = imginfo_obj['bands']
        band_info = bands_info[0]   # only care band one (suppose only have one band)
        histogram_info = band_info["histogram"]

        hist_count = histogram_info["count"]
        hist_min = histogram_info["min"]
        hist_max = histogram_info["max"]
        hist_buckets = histogram_info["buckets"]
        return (hist_count,hist_min,hist_max,hist_buckets)

    except KeyError:
        basic.outputlogMessage(str(KeyError))
        pass
    return (False, False,False,False)

    pass


def draw_dem_slope_hist(dem_path,slope_path,output):

    # get histogram of the dem
    dem_count,dem_min,dem_max,dem_buckets = get_hisogram_of_oneband_raster(dem_path)
    if dem_count is False:
        return False

    # get histogram of the slope
    slope_count,slope_min,slope_max,slope_buckets = get_hisogram_of_oneband_raster(slope_path)
    if slope_count is False:
        return False

    fig = plt.figure(figsize=(6,4)) #
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twiny()    #have another x-axis

    # plot slope histogram
    slope_y = np.array(slope_buckets)
    slope_x = np.linspace(slope_min, slope_max, slope_count)

    slope_per = 100.0 * slope_y / np.sum(slope_y)  # draw the percentage

    line_slope, = ax1.plot(slope_x,slope_per,'k-', label="Slope Histogram", linewidth=0.8)

    # marked the range of gully slope
    slope_range = [8.0, 17.4]
    for slope in slope_range:
        ax1.axvline(x=slope,color='k',linewidth=0.8,linestyle='--')
        ax1.text(slope, 0.15, '%.1f'%slope, rotation=90,fontsize=16)


    # ax1.set_xlabel("Slope ($^\circ$)",fontsize=15)
    ax1.yaxis.tick_right()
    # ax1.yaxis.set_label_position("right")
    # ax1.set_ylabel("Percentage (%)",fontsize=15)

    # plot dem histogram
    dem_y = np.array(dem_buckets)
    dem_y = np.delete(dem_y,0)
    dem_y = np.delete(dem_y, -1)
    dem_per = 100.0 * dem_y / np.sum(dem_y) # draw the percentage

    dem_x = np.linspace(dem_min, dem_max, dem_count)
    dem_x = np.delete(dem_x,0)
    dem_x = np.delete(dem_x, -1)

    line_dem, = ax2.plot(dem_x, dem_per,'r-', label="DEM Histogram", linewidth=0.8)
    # ax2.set_xlabel("Elevation (m)",color="red",fontsize=15)
    # ax2.spines['bottom'].set_color('blue')
    ax2.spines['top'].set_color('red')
    # ax2.xaxis.label.set_color('blue')
    ax2.tick_params(axis='x', colors='red')

    # marked the range of gully dem
    dem_range = [3526, 3667]
    for dem in dem_range:
        ax2.axvline(x=dem, color='r', linewidth=0.8, linestyle='--')
        ax2.text(dem-5, 1.79, str(dem), rotation=90, fontsize=16,color='r')

    print(np.sum(slope_y),np.sum(dem_y))


    # plt.gcf().subplots_adjust(bottom=0.15)  #add space for the buttom
    plt.gcf().subplots_adjust(top=0.8)  # the value range from [0,1], 1 is toppest, 0 is bottom
    # plt.gcf().subplots_adjust(left=0.15)
    # plt.gcf().subplots_adjust(right=0.15)

    # ax1.legend(loc="upper right")

    # fig.legend((line_slope,line_dem),('Slope Histogram', 'DEM Histogram'))
    ax1.legend((line_slope, line_dem), ('Slope', 'DEM'), fontsize=16,loc='upper center')

    plt.savefig(output,dpi=300)
    # plt.show()
    pass

def draw_image_histogram_oneband(image_path,output):

    CommandString = 'gdalinfo -json -hist -mm ' + image_path
    imginfo = basic.exec_command_string_output_string(CommandString)
    if imginfo is False:
        return False
    imginfo_obj = json.loads(imginfo)

    try:
        bands_info = imginfo_obj['bands']
        band_info = bands_info[0]   # only care band one (suppose only have one band)
        histogram_info = band_info["histogram"]

        hist_count = histogram_info["count"]
        hist_min = histogram_info["min"]
        hist_max = histogram_info["max"]
        hist_buckets = histogram_info["buckets"]

        hist_array = np.array(hist_buckets)
        hist_x = np.linspace(hist_min,hist_max,hist_count)
        hist_percent = 100.0*hist_array/np.sum(hist_array)

        print(np.sum(hist_array))
        # print(hist_percent)

        # matplotlib build-in color
        # b: blue
        # g: green
        # r: red
        # c: cyan
        # m: magenta
        # y: yellow
        # k: black
        # w: white

        # plt.figure(figsize=(12, 8))
        # color_used_count = 5
        # line_color = ['w', 'k'] #['b', 'g', 'r', 'c', 'm', 'y', 'k']
        # # linestyle = ['-','--','-.']
        # # linestyle = ['*', '+', 's', 'h', 'x', 'd', 'p', 'H', 'D']
        # ncount = hist_count
        #
        # # plot line
        # plt.ylim(0,2)
        plt.plot(list(hist_x), list(hist_percent), 'b-', label="label", linewidth=1.5)


        print(hist_x)
        print(hist_percent)





        # plt.xlabel("Distance (meter)")
        # plt.ylabel("Average Offset Of One Year (meter)")
        # plt.title("Offset meters Per Year of Jakobshavn glacier")
        # plt.ylim(0, 15000)
        # plt.legend()
        # plt.show()
        plt.savefig(output)


    except KeyError:
        basic.outputlogMessage(str(KeyError))
        pass
    return (False, False)

    pass

def main(options, args):

    shape_file = args[0]
    if io_function.is_file_exist(shape_file) is False:
        return False

    # draw_image_histogram_oneband("/Users/huanglingcao/Data/eboling/DEM/20160728-Large-DSM-NaN_slope.tif","slope_hist.jpg")
    # draw_image_histogram_oneband("/Users/huanglingcao/Data/eboling/DEM/20160728-Large-DSM-NaN.tif","dem_hist.jpg")

    # draw_dem_slope_hist("/Users/huanglingcao/Data/eboling/DEM/20160728-Large-DSM-NaN.tif",
    #                     "/Users/huanglingcao/Data/eboling/DEM/20160728-Large-DSM-NaN_slope.tif",
    #                     "dem_slope_histogram.jpg")


    draw_one_attribute_histogram(shape_file, "INarea", "Area ($m^2$)", "area.jpg")   #,hatch='-'
    draw_one_attribute_histogram(shape_file, "INperimete", "Perimeter (m)", "Perimeter.jpg")  #,hatch='\\'
    draw_one_attribute_histogram(shape_file, "ratio_w_h", "ratio of HEIGHT over WIDTH (W>H)", "ratio_w_h.jpg")
    draw_one_attribute_histogram(shape_file, "ratio_p_a", "ratio of $perimeter^2$ over area", "ratio_p_a.jpg")
    draw_one_attribute_histogram(shape_file, "circularit", "Circularity", "Circularity.jpg")  # ,hatch='.'

    # topography
    draw_one_attribute_histogram(shape_file, "dem_std", "standard variance of DEM", "dem_std.jpg")
    draw_one_attribute_histogram(shape_file, "dem_max", "maximum value of DEM (meter)", "dem_max.jpg")
    draw_one_attribute_histogram(shape_file, "dem_mean", "Mean Elevation (m)", "dem_mean.jpg")  # ,hatch='x'
    draw_one_attribute_histogram(shape_file, "dem_min", "minimum value of DEM (meter)", "dem_min.jpg")

    draw_one_attribute_histogram(shape_file, "slo_std", "standard variance of Slope", "slo_std.jpg")
    draw_one_attribute_histogram(shape_file, "slo_max", "maximum value of Slope ($^\circ$)", "slo_max.jpg")
    draw_one_attribute_histogram(shape_file, "slo_mean", "Mean Slope ($^\circ$)", "slo_mean.jpg") #,hatch='/'
    draw_one_attribute_histogram(shape_file, "slo_min", "minimum value of Slope ($^\circ$)", "slo_min.jpg")

    #hydrology
    draw_one_attribute_histogram(shape_file, "F_acc_std", "standard variance of Flow accumulation", "F_acc_std.jpg")
    draw_one_attribute_histogram(shape_file, "F_acc_max", "maximum value of Flow accumulation", "F_acc_max.jpg")
    draw_one_attribute_histogram(shape_file, "F_acc_mean", "mean value of Flow accumulation", "F_acc_mean.jpg")
    draw_one_attribute_histogram(shape_file, "F_acc_min", "minimum value of Flow accumulation", "F_acc_min.jpg")

    os.system("mv processLog.txt bins.txt")

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


#!/usr/bin/env python
# Filename: parameters.py
"""
introduction: get the parameter from file

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 06 May, 2016
"""

import sys,os
import basic_src.basic as basic
import basic_src.io_function as io_function
from optparse import OptionParser

saved_parafile_path ='para_default.ini'

#region basic function
def set_saved_parafile_path(path):
    if os.path.isfile(path) is False:
        print ("File not exist: "+os.path.abspath(path))
        raise IOError("File not exist: "+os.path.abspath(path))
        # sys.exit(1)
    global saved_parafile_path
    saved_parafile_path = path
# def set_output_basename(basename):
#     global output_basename
#     output_basename = basename
# def set_refchipW(_refchipW):
#     global refchipW
#     refchipW = _refchipW
# def set_refchipH(_refchipH):
#     global refchipH
#     refchipH = _refchipH
# def set_averageOffetperyear(_averageOffetperyear):
#     global averageOffetperyear
#     averageOffetperyear = _averageOffetperyear

def read_Parameters_file(parafile,parameter):
    try:
      inputfile = open(parafile, 'r')
    except IOError:
      raise IOError("Error: Open file failed, path: %s"%os.path.abspath(parafile))
    list_of_all_the_lines = inputfile.readlines()
    value = False
    for i in range(0,len(list_of_all_the_lines)):
        line = list_of_all_the_lines[i]
        if line[0:1] == '#' or len(line) < 2:
            continue
        lineStrs = line.split('=')
        lineStrleft = lineStrs[0].strip()     #remove ' ' from left and right
        if lineStrleft.upper() == parameter.upper():
            value = lineStrs[1].strip()
            break
    inputfile.close()
    # don't do this
    # global saved_parafile_path
    # saved_parafile_path = parafile
    return value


def write_Parameters_file(parafile,parameter,new_value):
    try:
      inputfile = open(parafile, 'r')
    except IOError:
      raise IOError("Error: Open file failed, path: %s" % os.path.abspath(parafile))
    list_of_all_the_lines = inputfile.readlines()
    value = False
    for i in range(0,len(list_of_all_the_lines)):
        line = list_of_all_the_lines[i]
        if line[0:1] == '#' or len(line) < 2:
            continue
        lineStrs = line.split('=')
        lineStrleft = lineStrs[0].strip()     #remove ' ' from left and right
        if lineStrleft.upper() == parameter.upper():
            list_of_all_the_lines[i] = lineStrleft + " = " +str(new_value) + "\n"
            break
    inputfile.close()

    # write the new file and overwrite the old one
    try:
      outputfile = open(parafile, 'w')
    except IOError:
      raise IOError("Error: Open file failed, path: %s" % os.path.abspath(parafile))
    outputfile.writelines(list_of_all_the_lines)
    outputfile.close()
    return True



def get_string_parameters(parafile,name):
    if parafile =='':
        parafile = saved_parafile_path
    result = read_Parameters_file(parafile,name)
    if result is False:
        raise ValueError('get %s parameter failed'%name)
    else:
        return result

def get_string_parameters_None_if_absence(parafile,name):
    if parafile =='':
        parafile = saved_parafile_path
    result = read_Parameters_file(parafile,name)
    if result is False or len(result) < 1:
        return None
    else:
        return result

def get_directory_None_if_absence(parafile,name):
    value = get_string_parameters_None_if_absence(parafile,name)
    if value is None:
        return None
    return os.path.expanduser(value)

def get_directory(parafile,name):
    value = get_string_parameters_None_if_absence(parafile,name)
    if value is None:
        raise ValueError('%s not set in %s'%(name,parafile))
    return os.path.expanduser(value)

def get_file_path_parameters_None_if_absence(parafile,name):
    value = get_string_parameters_None_if_absence(parafile, name)
    if value is None:
        return None
    return os.path.expanduser(value)

def get_file_path_parameters(parafile,name):
    value = get_file_path_parameters_None_if_absence(parafile, name)
    if value is None:
        raise ValueError('%s not set in %s'%(name,parafile))
    return os.path.expanduser(value)


def get_bool_parameters_None_if_absence(parafile,name):
    if parafile =='':
        parafile = saved_parafile_path
    result = read_Parameters_file(parafile,name)
    if result is False or len(result) < 1:
        return None
    if result.upper()=='YES':
        return True
    else:
        return False

def get_bool_parameters(parafile,name):
    value = get_bool_parameters_None_if_absence(parafile,name)
    if value is None:
        raise ValueError(' %s not set in %s' % (name, parafile))
    return value


def get_digit_parameters_None_if_absence(parafile,name,datatype):
    if parafile =='':
        parafile = saved_parafile_path
    result = read_Parameters_file(parafile,name)
    if result is False or len(result) < 1:
        return None
    try:
        if datatype == 'int':
            digit_value = int(result)
        else:
            digit_value = float(result)
    except ValueError:
            raise ValueError('convert %s to digit failed , exit'%(name))

    return digit_value

def get_digit_parameters(parafile,name,datatype):
    value = get_digit_parameters_None_if_absence(parafile, name, datatype)
    if value is None:
        raise ValueError(' %s not set in %s'%(name, parafile))
    return value


def get_string_list_parameters_None_if_absence(parafile,name):
    str_value = get_string_parameters(parafile, name)
    attributes_list = []

    # if the list is in a txt file
    if str_value.endswith('.txt') and len(str_value.split(',')) == 1:
        with open(str_value, 'r') as f_obj:
            lines = f_obj.readlines()
            lines = [item.strip() for item in lines]
            return lines

    attributes_init = str_value.split(',')
    if len(attributes_init) < 1:
        return None
    else:
        for att_str in attributes_init:
            str_temp = att_str.strip()  # remove certain characters (such as whitespace) from the left and right parts of strings
            if len(str_temp) > 0:
                attributes_list.append(str_temp)
        if len(attributes_list) < 1:
            return None
        else:
            return attributes_list

def get_string_list_parameters(parafile,name):
    str_value = get_string_list_parameters_None_if_absence(parafile,name)
    if str_value is None or len(str_value) < 1:
        raise ValueError('No inference area is set in %s' % parafile)
    return str_value

#region input and output setting
def get_input_image_path(parafile=''):
    return get_string_parameters(parafile, 'input_image_path')

def get_segment_project_folder(parafile=''):
    return get_string_parameters(parafile, 'segment_project_folder')

def get_input_image_rescale(parafile=''):
    return get_digit_parameters(parafile,'input_image_rescale',None,'float')

def get_input_ground_truth_image(parafile=''):
    return get_string_parameters(parafile, 'input_ground_truth_image')

def get_dem_file(parafile=''):
    return get_string_parameters(parafile, 'dem_file')

def get_slope_file(parafile=''):
    return get_string_parameters(parafile, 'slope_file')
def get_aspect_file(parafile=''):
    return get_string_parameters(parafile, 'aspect_file')

def get_flow_accumulation(parafile=''):
    return get_string_parameters(parafile, 'flow_accumulation')


#endregion


def get_QGIS_install_folder(parafile=''):
    return get_string_parameters(parafile, 'QGIS_install_folder')

### feature extraction Parameters Setting
def get_sfs_texture_spethre(parafile=''):
    return get_digit_parameters(parafile, 'sfs_texture_spethre', None, 'int')

#end feature extraction Parameters Setting

## target extraction (classification) Parameters Setting
def get_attributes_used(parafile=''):
    attributes_str =  get_string_parameters(parafile, 'attributes_used')
    attributes_list = []
    attributes_init = attributes_str.split(',')
    if len(attributes_init) < 1:
        return False
    else:
        for att_str in attributes_init:
            str_temp = att_str.strip()  # remove certain characters (such as whitespace) from the left and right parts of strings
            if len(str_temp) > 0:
                attributes_list.append(str_temp)
        if len(attributes_list) < 1:
            return False
        else:
            return attributes_list

def get_classifier(parafile=''):
    return get_string_parameters(parafile, 'classifier')

def get_raster_example_file(parafile=''):
    return get_string_parameters(parafile, 'raster_example_file')

#end target extraction  (classification) Parameters Setting



### Post processing and evaluation Parameters
def get_minimum_gully_area(parafile=''):
    return get_digit_parameters(parafile, 'minimum_gully_area', 'float')

def get_maximum_ratio_width_height(parafile=''):
    return get_digit_parameters(parafile, 'maximum_ratio_width_height', 'float')

def get_minimum_ratio_perimeter_area(parafile=''):
    return get_digit_parameters(parafile, 'minimum_ratio_perimeter_area', 'float')

def get_b_keep_holes(parafile=''):
    return get_bool_parameters(parafile, 'b_keep_holes' )

def get_validation_shape(parafile=''):
    return get_string_parameters(parafile, 'validation_shape')

def get_IOU_threshold(parafile=''):
    return get_digit_parameters(parafile, 'IOU_threshold', 'float')

#end Post processing and evaluation Parameters


### Parameters for image co-registration
def get_required_minimum_tiepoint_number(parafile=''):
    return get_digit_parameters(parafile, 'required_minimum_tiepoint_number', 'int')

def get_acceptable_maximum_RMS(parafile=''):
    return get_digit_parameters(parafile, 'acceptable_maximum_RMS', 'float')

def get_gdalwarp_polynomial_order(parafile=''):
    return get_digit_parameters(parafile, 'gdalwarp_polynomial_order', 'int')

def get_exec_dir(parafile=''):
    return get_string_parameters(parafile,'exec_dir')

def get_draw_tie_points_rms_vector_scale(parafile=''):
    return get_digit_parameters(parafile, 'draw_tie_points_rms_vector_scale', 'float')

#end Post processing and evaluation Parameters

def test_readparamters():
    parafile = '/Users/huanglingcao/Data/offset_landsat_auto_test/para.txt'

    return True

def main():
    usage = "usage: %prog [options] parameter_name"
    parser = OptionParser(usage=usage, version="1.0 2017-10-21")

    parser.add_option("-p", "--para",
                      action="store", dest="para_file",
                      help="the parameters file")
    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)

    # set parameters files
    if options.para_file is None:
        print('error, no parameters file')
        parser.print_help()
        sys.exit(2)
    else:
        set_saved_parafile_path(options.para_file)

    # read any parameter to a string
    para_name = args[0]
    value_str = get_string_parameters("", para_name)

    #output result to stdout
    print(value_str)

    # sys.exit(value_str)
    return value_str



if __name__=='__main__':
    # test_readparamters()
    main()





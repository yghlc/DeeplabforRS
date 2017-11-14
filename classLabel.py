#!/usr/bin/env python3
# Filename: classLabel 
"""
introduction: convert the class type to a index which can be install as a pixel value

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 21 February, 2017
"""

import basic_src.basic as basic
from optparse import OptionParser
import sys

import parameters

# class_label = {'gully': 1, 'unknown': 0,
#                'Bareland':2, 'road':3}

#lower case
class_label = ['null','gully','land','grass','bareland','road']

def get_class_label(index):
    """
    input a class index(integer), output the label string
    :param index: class index
    :return: a string represents the class
    """
    if isinstance(index,str):
        index = int(index)
        # print(type(index))
    if index < len(class_label):
        return class_label[index]
    basic.outputlogMessage('class index: %d not found in the class list' % index)
    assert (False)
    return False

def get_class_index(label):
    """
    input a class label string, (integer), output the index
    :param label: class label(string)
    :return: a integer represents the class, False Otherwise
    """
    if isinstance(label,str) is False:
        basic.outputlogMessage('input label must be a string')
        assert(False)
    length = len(class_label)
    for i in range(0,length):
        if label.lower()==class_label[i]:
            return i
    #if not found
    basic.outputlogMessage('class label: %s not found in the class list'%label)
    assert(False)
    return False


def output_classLabel_to_txt(save_path):
    """
    output class Label and its index to txt file
    :param save_path: txt file path
    :return: True if successful, False Otherwise
    """
    file_obj = open(save_path,'w')
    length = len(class_label)
    for i in range(0,length):
        line = '%d:%s'%(i,class_label[i])
        file_obj.writelines(line+'\n')
    return True


def main(options, args):
    class_raster = options.classraster
    class_shp = options.class_shp
    outputshp = args[0]

    # if class_raster is not None:
    #     basic.outputlogMessage('class raster file exist, ignore class_shp')
    #     return obia_classify.add_traning_example_from_raster(outputshp,class_raster)
    # elif class_shp is not None:
    #     if options.para_file is None:
    #         class_raster = 'raster_class.tif'
    #     else:
    #         parameters.set_saved_parafile_path(options.para_file)
    #         class_raster = parameters.get_raster_example_file()
    #
    #     if obia_classify.convert_training_examples_from_shp_to_raster(class_shp, class_raster) is True:
    #         return obia_classify.add_traning_example_from_raster(outputshp, class_raster)

    pass

if __name__=='__main__':
    usage = "usage: %prog [options] shpWithout_class.shp"
    parser = OptionParser(usage=usage, version="1.0 2017-3-14")
    parser.description = 'Introduction: Transfer class label of each polygon ' \
                         'from a shape file containing class labels to a new shape file  '
    parser.add_option("-p", "--para",
                      action="store", dest="para_file",
                      help="the parameters file")
    parser.add_option("-i", "--class_shp",
                      action="store", dest="class_shp",
                      help="shapefile containing class label, Please assign this value if you have one")

    parser.add_option("-r", "--class_raster",
                      action="store", dest="classraster",
                      help="raster file containing class label, Please assign this value if you have one")

    # parser.add_option("-s", "--used_file", action="store", dest="used_file",
    #                   help="the selectd used files,only need when you set --action=2")
    # parser.add_option('-o', "--output", action='store', dest="output",
    #                   help="the output file,only need when you set --action=2")

    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)

    # if options.para_file is None:
    #     basic.outputlogMessage('error, parameter file is required')
    #     sys.exit(2)

    main(options, args)


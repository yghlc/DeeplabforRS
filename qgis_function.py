#!/usr/bin/env python
# Filename: qgis_function 
"""
introduction: use the function of QGIS, need python2

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 03 November, 2016
"""

import basic_src.basic as basic
import basic_src.io_function as io_function
import os,sys
from optparse import OptionParser
# import parameters

#qgis  if change interpreter to python3, then pycharm complain it can not find qgis and processing
from qgis.core import *
import processing
from processing.core.Processing import Processing

class qgis_opeation(object):
    qgis_install_folder = "/usr"    #ubuntu
    #qgis_install_folder = "/Applications/QGIS.app/Contents/MacOS"    # mac
    # qgis_install_folder = parameters.get_QGIS_install_folder()

    def __init__(self):
        self.__qgis_app = None # qgis environment

        pass


    def __del__(self):
        if self.__qgis_app is not None:
            basic.outputlogMessage("Release QGIS resource")
            self.__qgis_app.exitQgis()

    def initQGIS(self):
        basic.outputlogMessage("initial QGIS resource")
        #check qgis install
        b_found_qgis = False
        if os.path.isfile(os.path.join(qgis_opeation.qgis_install_folder,'QGIS')) is True:
            b_found_qgis = True
        if os.path.isfile(os.path.join(qgis_opeation.qgis_install_folder,'bin','qgis')) is True:
            b_found_qgis = True
        if b_found_qgis is False:
            basic.outputlogMessage('no QIGS installed in %s'%qgis_opeation.qgis_install_folder)
            return False

        self.__qgis_app = QgsApplication([], True)
        QgsApplication.setPrefixPath(qgis_opeation.qgis_install_folder, True)
        QgsApplication.initQgis()

        # providers = QgsProviderRegistry.instance().providerList()
        # for provider in providers:
        #     print provider
        Processing.initialize()
        Processing.updateAlgsList()
        basic.outputlogMessage("initial QGIS resource completed")
        pass

    def get_polygon_shape_info(self,input_shp,out_box,bupdate=False):
        """
        get Oriented minimum bounding box for a polygon shapefile,
        and update the shape information based on oriented minimum bounding box to
        the input shape file
        :param input_shp: input polygon shape file
        :param out_box: output Oriented minimum bounding box shape file
        :param bupdate: indicate whether update the original input shapefile
        :return:True is successful, False Otherwise
        """
        if io_function.is_file_exist(input_shp) is False:
            return False

        if self.__qgis_app is None:
            try:
                self.initQGIS()
            except :
                basic.outputlogMessage("initial QGIS error")
                self.__qgis_app = None
                return False

        processing.runalg("qgis:orientedminimumboundingbox", input_shp, True, out_box)

        if os.path.isfile(out_box) is False:
            basic.outputlogMessage("error: result file not exist, getting orientedminimumboundingbox failed")
            return False

        #update shape info to input shape file
        if bupdate is True:
            pass

def main(options, args):
    if len(args)<2:
        basic.outputlogMessage('error: we need to arguments')
        return False
    input_file =  args[0]
    output_file = args[1]
    qgis_obj = qgis_opeation()
    qgis_obj.get_polygon_shape_info(input_file,output_file)

    pass


if __name__=='__main__':
    usage = "usage: %prog [options] input_file output_file"
    parser = OptionParser(usage=usage, version="1.0 2016-11-03")
    parser.add_option("-p", "--para",
                      action="store", dest="para_file",
                      help="the parameters file")
    # parser.add_option("-s", "--used_file", action="store", dest="used_file",
    #                   help="the selectd used files,only need when you set --action=2")
    # parser.add_option('-o', "--output", action='store', dest="output",
    #                   help="the output file,only need when you set --action=2")

    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)
    # parameters.set_saved_parafile_path(parser.para_file)

    main(options, args)

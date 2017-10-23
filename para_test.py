#!/usr/bin/env python
# Filename: para_test 
"""
introduction: perform test different value of parameters, and see the influence in the results

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 23 October, 2017
"""

import os,sys

HOME = os.path.expanduser('~')
codes_path = HOME +'/codes/PycharmProjects/DeeplabforRS'
sys.path.insert(0, codes_path)

import parameters
import basic_src.basic as basic

para_file = "para.ini"

patchSize = 65
while(patchSize<460):
    basic.outputlogMessage("Test on Patch size: patch_width=%d, patch_height=%d"%(patchSize,patchSize))

    # change the para.ini file
    parameters.write_Parameters_file(para_file,"patch_width",patchSize)
    parameters.write_Parameters_file(para_file, "patch_height", patchSize)



    #running the model
    if os.path.isfile("./whole_process.sh") is False:
        basic.outputlogMessage("Please copy whole_process.sh file first")
        sys.exit(1)
    os.system("./whole_process.sh")

    #move results, only the shapefile
    os.system("rm post_pro_val_result/*.png")
    os.system("rm post_pro_val_result/*.tif")
    os.system("mv post_pro_val_result post_pro_val_result_patch"+str(patchSize))

    # update for next loop
    patchSize = patchSize + 30










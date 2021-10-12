#!/usr/bin/env python
# Filename: RSImageProcess.py 
"""
introduction: contains some image operation such as subset, mosaic

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 05 May, 2016
"""

# support for python3: import the script in the same dir. hlc 2019-Jan-15
import sys,os
py_dir=os.path.dirname(os.path.realpath(__file__))
# print(py_dir)
sys.path.append(py_dir)

from RSImage import RSImageclass
import numpy,basic,io_function,RSImage,geometryProcess
from numpy import *
import struct,os
import map_projection

class RSImgProclass(object):
    def __init__(self):
        self.imgpath = ''
        self.img__obj = None    #RSImageclass  object

    def __del__(self):
        # close dataset
        # print 'RSImageclass__del__'
        self.img__obj = None

    def Read_Image_band_data_to_numpy_array_all_pixel(self,bandindex,image_path):
        if io_function.is_file_exist(image_path) is False:
            return False
        self.img__obj =  RSImageclass()
        if self.img__obj.open(image_path) is False:
            return False
        width = self.img__obj.GetWidth()
        height = self.img__obj.GetHeight()
        return self.__Read_band_data_to_numpy_array(bandindex,0,0,width,height,self.img__obj)

    def __Read_Image_band_data_to_numpy_array(self,bandindex,xoff,yoff,width,height,image_path):
        return True

    def __Read_band_data_to_numpy_array(self,bandindex,xoff,yoff,width,height,image_obj=None):
        if image_obj is None:
            image_obj = self.img__obj
        offsetvaluestr = image_obj.ReadbandData(bandindex,xoff,yoff,width,height,image_obj.GetGDALDataType())  #first band offset, may be xoffset
        if offsetvaluestr is False:
            return False
        # offsetvalue = None
        # print image_obj.GetGDALDataType()
        if image_obj.GetGDALDataType() == 3:    #GDT_Int16
            offsetvalue  = struct.unpack('h'*width*height, offsetvaluestr)
        elif image_obj.GetGDALDataType() == 6:
            offsetvalue  = struct.unpack('f'*width*height, offsetvaluestr)
        else:
            basic.outputlogMessage('error: not support datatype currently')
            return False

        return numpy.asarray(offsetvalue)


    def statistic_element_count(self,value,myarray):
        loc_nodata= numpy.where(numpy.fabs(myarray-value)<0.001)
        loc_nodatanum = numpy.array(loc_nodata).size
        return loc_nodatanum

    def statistic_not_element_count(self,not_value,myarray):
        loc_not_value = numpy.where(numpy.fabs(myarray - not_value)>0.0001)
        loc_not_value_num = numpy.array(loc_not_value).size
        return loc_not_value_num

    def statistic_pixel_count(self,pixel_value,RSImageclass_object):

        return True

    def compose_two_image(self,main_image,second_image,nodata):

        if io_function.is_file_exist(main_image) is False:
            return False
        if io_function.is_file_exist(second_image) is False:
            return False
        main_img =  RSImageclass()
        if main_img.open(main_image) is False:
            return False
        width_main = main_img.GetWidth()
        height_main = main_img.GetHeight()
        bandcount_main = main_img.GetBandCount()

        sec_img =  RSImageclass()
        if sec_img.open(second_image) is False:
            return False
        width_sec = sec_img.GetWidth()
        height_sec = sec_img.GetHeight()
        bandcount_sec = sec_img.GetBandCount()

        if width_main!=width_sec or height_main!=height_sec or bandcount_main!=bandcount_sec:
            basic.outputlogMessage('Error: The dimension of two composed images is different')
            return False
        if main_img.GetGDALDataType() != sec_img.GetGDALDataType() or main_img.GetGDALDataType() != 6:
            basic.outputlogMessage('Error: The Data type of two composed imagaes is different or is not float')
            return False

        outputfile = io_function.get_name_by_adding_tail(main_image,'comp')
        imagenew = RSImageclass()
        width = width_main
        height = height_main
        if not imagenew.New(outputfile,width,height,bandcount_main ,main_img.GetGDALDataType()):
            return False
        for i in range(0,bandcount_main):
            bandindex = i+1
            band_main_str = main_img.ReadbandData(bandindex,0,0,width,height,main_img.GetGDALDataType())
            band_sec_str =  sec_img.ReadbandData(bandindex,0,0,width,height,sec_img.GetGDALDataType())

            band_main_data  = struct.unpack('f'*width*height, band_main_str)
            band_main_numpy = numpy.asarray(band_main_data)

            band_sec_data  = struct.unpack('f'*width*height, band_sec_str)
            band_sec_numpy = numpy.asarray(band_sec_data)

            compose_loc = numpy.where( (numpy.fabs(band_main_numpy-nodata)<0.0001) & (numpy.fabs(band_sec_numpy-nodata)>0.0001))
            band_main_numpy[compose_loc] = band_sec_numpy[compose_loc]
            basic.outputlogMessage('outputfortest2: compose_loc_num = %d'%numpy.array(compose_loc).size)

            templist = band_main_numpy.tolist()
            band_composed_str = struct.pack('%sf'%width*height,*templist)
            if imagenew.WritebandData(bandindex,0,0,width,height,band_composed_str,imagenew.GetGDALDataType()) is False:
                return False
            imagenew.SetBandNoDataValue(bandindex,nodata)

        imagenew.SetGeoTransform(main_img.GetGeoTransform())
        imagenew.SetProjection(main_img.GetProjection())

        main_img = None
        sec_img =None
        imagenew = None

        return outputfile

def mosaic_crop_images_gdalwarp(raster_files,outputfile,src_nodata=None,dst_nodata=None,min_x=None,min_y=None, max_x=None, max_y=None,
                                xres=None,yres=None,resampling_method='min', o_format='GTiff',
                                compress=None,tiled=None, bigtiff=None, thread_num=None):
    '''
    create a mosaic from multiple input raster using gdalwarp, crop if min_x, min_y, max_x, max_y are valid
    Args:
        raster_files: input raster list
        outputfile: output file
        src_nodata:
        dst_nodata:
        min_x:
        min_y:
        max_x:
        max_y:
        xres:
        yres:
        resampling_method: including, average, mode, max, min, med, q1, q3, sum  https://gdal.org/programs/gdalwarp.html
        o_format: output format, default is GTiff, GeoTIFF File Format. Use "VRT": GDAL Virtual Format to save disk storage

    Returns:

    '''

    if isinstance(raster_files,list) is False:
        # raise ValueError('the type of raster_files must be list')
        basic.outputlogMessage('the type of raster_files must be list')
        return False

    if len(raster_files)<1:
        # raise ValueError('file count less than 1')
        basic.outputlogMessage('file count less than 1')
        return False

    CommandString = 'gdalwarp -r ' + resampling_method + ' -of ' + o_format

    if src_nodata != None:
        CommandString += ' -srcnodata ' +  str(src_nodata)
    if dst_nodata != None:
        CommandString += ' -dstnodata ' + str(dst_nodata)

    if min_x != None and min_y != None and max_x != None and max_y!= None:
        CommandString += ' -te ' + str(min_x)+' '+str(min_y)+' '+str(max_x)+' '+str(max_y)

    if xres !=None and yres!=None:
        CommandString += ' -tr ' + str(xres) + ' ' +str(yres)

    if compress != None:
        CommandString += ' -co ' + 'compress=%s'%compress       # lzw
    if tiled != None:
        CommandString += ' -co ' + 'TILED=%s'%tiled     # yes
    if bigtiff != None:
        CommandString += ' -co ' + 'bigtiff=%s' % bigtiff  # IF_SAFER

    if thread_num != None:
        CommandString += ' -multi -wo NUM_THREADS=%d '%thread_num

    inputfiles = ' '.join(raster_files)
    CommandString += ' ' + inputfiles + ' ' + outputfile

    return basic.exec_command_string_one_file(CommandString,outputfile)


def mosaics_images(raster_files,outputfile,nodata=None,compress=None,tiled=None, bigtiff=None):
    """
    mosaic a set of images. All the images must be in the same coordinate system and have a matching number of bands,
    Args:
        raster_files:a set of images with same coordinate system and have a matching number of bands, list type
        outputfile: the mosaic result file

    Returns: the result path if successful, False otherwise

    """
    if isinstance(raster_files,list) is False:
        basic.outputlogMessage('the type of raster_files must be list')
        return False
    if len(raster_files)<2:
        basic.outputlogMessage('file count less than 2')
        return False

    inputfile = ''
    for i in range(0,len(raster_files)):
        if io_function.is_file_exist(raster_files[i]) is False:
            return False
        inputfile = inputfile + ' ' + raster_files[i]
    CommandString = 'gdal_merge.py ' + inputfile +  ' -o '+ outputfile
    if nodata is not None:
        CommandString += ' -n ' + str(nodata)
        CommandString += ' -a_nodata ' + str(nodata)

    if compress != None:
        CommandString += ' -co ' + 'compress=%s'%compress       # lzw
    if tiled != None:
        CommandString += ' -co ' + 'TILED=%s'%tiled     # yes
    if bigtiff != None:
        CommandString += ' -co ' + 'bigtiff=%s' % bigtiff  # IF_SAFER

    return basic.exec_command_string_one_file(CommandString,outputfile)

def subset_image_baseimage(output_file,input_file,baseimage,same_res=False,resample_m='bilinear'):
    """
    subset a image base on the extent of another image
    Args:
        output_file:the result file
        input_file:the image need to subset
        baseimage:the base image which provide the extend for subset
        same_res: if true, then will resample the output to the resolution of baseimage, otherwise, keep the resolution

    Returns:True is successful, False otherwise

    """
    (ulx,uly,lrx,lry) = RSImage.get_image_proj_extent(baseimage)
    if ulx is False:
        return False
    # check the save folder is valid or not
    save_dir = os.path.dirname(output_file)
    if len(save_dir) < 1:
        basic.outputlogMessage('output save to current folder')
    else:
        basic.outputlogMessage('result save to %s'%save_dir)

    img_obj = RSImageclass()
    if same_res:
        img_obj.open(baseimage)
    else:
        img_obj.open(input_file)    # the resolution should keep the same
    xres = img_obj.GetXresolution()
    yres = img_obj.GetYresolution()
    img_obj=None

    if subset_image_projwin(output_file,input_file,ulx,uly,lrx,lry,xres=xres,yres=yres,resample_m=resample_m,
                            compress='lzw', tiled='yes', bigtiff='if_safer') is False:
        return False
    return True

def subset_image_projwin(output,imagefile,ulx,uly,lrx,lry,resample_m='bilinear',dst_nondata=0,xres=None,yres=None,
                         o_format='GTiff',compress=None, tiled=None, bigtiff=None,thread_num=None):
    #bug fix: the origin (x,y) has a difference between setting one when using gdal_translate to subset image 2016.7.20
    # CommandString = 'gdal_translate  -r bilinear  -eco -projwin ' +' '+str(ulx)+' '+str(uly)+' '+str(lrx)+' '+str(lry)\
    # + ' '+imagefile + ' '+output
    xmin = ulx
    ymin = lry
    xmax = lrx
    ymax = uly
    # if xres is None or yres is None:
    #     CommandString = 'gdalwarp -r bilinear -te  ' +' '+str(xmin)+' '+str(ymin)+' '+str(xmax)+' '+str(ymax)\
    #     + ' ' + ' -dstnodata '+ str(dst_nondata) + ' '+imagefile + ' '+output
    # else:
    #     CommandString = 'gdalwarp -r bilinear -te  ' + ' ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) \
    #                     + ' -tr ' +str(xres) + ' ' +str(yres) +' ' + ' -dstnodata '+ str(dst_nondata) + ' '+ imagefile + ' ' + output

    # update on 2018 Oct 20, we should not set nodata in subset opertion. It will copy from the source dataset

    CommandString = 'gdalwarp -r %s '%resample_m + ' -of ' + o_format
    CommandString += ' -te ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax)

    # if src_nodata != None:
    #     CommandString += ' -srcnodata ' +  str(src_nodata)
    # if dst_nodata != None:
    #     CommandString += ' -dstnodata ' + str(dst_nodata)

    if xres !=None and yres!=None:
        CommandString += ' -tr ' + str(xres) + ' ' +str(yres)

    if compress != None:
        CommandString += ' -co ' + 'compress=%s'%compress       # lzw
    if tiled != None:
        CommandString += ' -co ' + 'TILED=%s'%tiled     # yes
    if bigtiff != None:
        CommandString += ' -co ' + 'bigtiff=%s' % bigtiff  # IF_SAFER

    if thread_num != None:
        CommandString += ' -multi -wo NUM_THREADS=%d '%thread_num

    CommandString += ' '+ imagefile + ' ' + output

    return basic.exec_command_string_one_file(CommandString,output)

def subset_image_srcwin(output,imagefile,xoff,yoff,xsize,ysize):
    CommandString = 'gdal_translate  -r bilinear  -eco -srcwin ' +' '+str(xoff)+' '+str(yoff)+' '+str(xsize)+' '+str(ysize)\
    + ' '+imagefile + ' '+output
    return basic.exec_command_string_one_file(CommandString,output)

def subsetLandsat7_Jakobshavn_shape(imagefile,shapefile,bkeepmidfile):
    return subset_image_by_shapefile(imagefile,shapefile,bkeepmidfile)

def subset_image_by_polygon_box_image_min(output, imagefile, polygon, resample_m='bilinear', xres=None, yres=None,
                                          o_format='GTiff',compress=None, tiled=None, bigtiff=None,thread_num=None):
    '''
    crop a image using the box of a shapely polygon. The polygon and image should in the same projection, not check here
    # if the image extent is small then box, then use image extent
    Args:
        output:
        imagefile:
        polygon:
        xres:
        yres:

    Returns: output path if successful, False otherwise

    '''

    # #  polygon.exterior.coords
    minx, miny, maxx, maxy =  polygon.bounds    # (minx, miny, maxx, maxy)
    # print(minx, miny, maxx, maxy)
    img_extent = RSImage.get_image_proj_extent(imagefile)  # (ulx,uly,lrx,lry)
    im_minx, im_maxy, im_maxx, im_miny = img_extent

    # chose the smallest extent
    minx = max(minx,im_minx)
    maxx = min(maxx,im_maxx)
    miny = max(miny,im_miny)
    maxy = min(maxy,im_maxy)

    if minx >= maxx or miny >= maxy:
        basic.outputlogMessage('Warning, out of extent, Crop %s failed' % imagefile)
        return False

    result = subset_image_projwin(output,imagefile,minx, maxy, maxx, miny, resample_m=resample_m, xres=xres,yres=yres,
                                  o_format=o_format,compress=compress, tiled=tiled, bigtiff=bigtiff,thread_num=thread_num)

    if result is False:
        basic.outputlogMessage('Warning, Crop %s failed'%imagefile)
        return False
    return result


def subset_image_by_polygon_box(output, imagefile, polygon, resample_m='bilinear', xres=None, yres=None,
                                o_format='GTiff',compress=None, tiled=None, bigtiff=None,thread_num=None):
    '''
    crop a image using the box of a shapely polygon. The polygon and image should in the same projection, not check here
    Args:
        output:
        imagefile:
        polygon:
        xres:
        yres:

    Returns: output path if successful, False otherwise

    '''

    # #  polygon.exterior.coords
    minx, miny, maxx, maxy =  polygon.bounds    # (minx, miny, maxx, maxy)
    # print(minx, miny, maxx, maxy)
    result = subset_image_projwin(output,imagefile,minx, maxy, maxx, miny, resample_m=resample_m, xres=xres,yres=yres,
                                  o_format=o_format,compress=compress, tiled=tiled, bigtiff=bigtiff, thread_num=thread_num)

    if result is False:
        basic.outputlogMessage('Warning, Crop %s failed'%imagefile)
        return False
    return result

def subset_image_by_shapefile(imagefile,shapefile,bkeepmidfile=True, overwrite=False, format='GTiff', save_path=None ):
    """
    subset an image by polygons contained in the shapefile
    the shapefile and imagefile may have different projections, the gdalwarp can handle
    Args:
        imagefile:input image file path
        shapefile:input shapefile contains polygon
        bkeepmidfile:indicate whether keep middle file
        format: output format,  default is GTiff, GeoTIFF File Format. Use "VRT": GDAL Virtual Format to save disk storage

    Returns:output file name if succussful, False Otherwise

    """
    if io_function.is_file_exist(imagefile) is False:
        return False
    if io_function.is_file_exist(shapefile) is False:
        return False

    if save_path is None:
        Outfilename = io_function.get_name_by_adding_tail(imagefile,'vsub')
    else:
        Outfilename = save_path

    # ds = ogr.Open(shapefile)
    # lyr = ds.GetLayer(0)
    # lyr.ResetReading()
    # ft = lyr.GetNextFeature()

    # subprocess.call(['gdalwarp', imagefile, Outfilename, '-cutline', shapefile,\
    #                       '-crop_to_cutline'])

    if overwrite is False and os.path.isfile(Outfilename):
        basic.outputlogMessage('warning, crop file: %s already exist, skip'%Outfilename)
        return Outfilename

    orgimg_obj = RSImageclass()
    if orgimg_obj.open(imagefile) is False:
        return False
    x_res = abs(orgimg_obj.GetXresolution())
    y_res = abs(orgimg_obj.GetYresolution())

    CommandString = 'gdalwarp '+' -tr ' + str(x_res) + '  '+ str(y_res)+ ' -of ' + format + ' ' + imagefile +' ' + Outfilename +' -cutline ' +shapefile +' -crop_to_cutline ' + ' -overwrite '
    if basic.exec_command_string_one_file(CommandString,Outfilename) is False:
        return False

    # while ft:
    #     country_name = ft.GetFieldAsString('admin')
    #     outraster = imagefile.replace('.tif', '_%s.tif' % country_name.replace(' ', '_'))
    #     subprocess.call(['gdalwarp', imagefile, Outfilename, '-cutline', shapefile,
    #                      '-crop_to_cutline', '-cwhere', "'admin'='%s'" % country_name])
    #
    #     ft = lyr.GetNextFeature()

    if not bkeepmidfile:
        io_function.delete_file_or_dir(imagefile)
        os.remove(imagefile)

    if io_function.is_file_exist(Outfilename):
        return Outfilename
    else:
        # basic.outputlogMessage(result)
        basic.outputlogMessage('The version of GDAL must be great than 2.0 in order to use the r option ')
        return False



def mask_pixel_out_polygon(imagefile,shapefile,burnvalue,bkeepmidfile):
    """
    set other pixel outside the polygon as zero, will modify the original data
    Args:
        imagefile:the image need to be masked
        shapefile:the shapefile contains polygon
        burnvalue:masked value
        bkeepmidfile:whether keep middle file

    Returns:True if successful, False Otherwise

    """
    #inquiry imagefile srs
    target_srs = map_projection.get_raster_or_vector_srs_info_proj4(imagefile);
    if target_srs is False:
        return False
    polygon_srs = map_projection.get_raster_or_vector_srs_info_proj4(shapefile);
    if polygon_srs is False:
        return False
    polygon_path = shapefile
    #convert shapefile srs
    if target_srs != polygon_srs:
        # t_file = os.path.splitext(shapefile)[0] + '_trans.shp'
        t_file = os.path.basename(polygon_path).split('.')[0]+'_trans.shp'
        if os.path.isfile(t_file) is False:
            map_projection.transforms_vector_srs(shapefile,target_srs,t_file)
        else:
            basic.outputlogMessage('%s already exist'%t_file)
        polygon_path = t_file
    if os.path.isfile(polygon_path) is False:
        return False

    basic.outputlogMessage('mask the pixel out the interesting region as value : '+ str(burnvalue))
    #mask the pixel outside polygon as zero
    layername = os.path.basename(polygon_path).split('.')[0]
    CommandString = 'gdal_rasterize -b 1  -at -i  -burn '+ str(burnvalue) + \
    ' -l '+ layername + ' '+polygon_path +' ' + imagefile
    (status, result) = basic.exec_command_string(CommandString)
    basic.outputlogMessage(result)

    if result.find('done'):
        return True
    else:
        return False

def convert_image_to_gray_auto(output_image,input_image):
    """
    convert inputed image to 8bit
    Args:
        output_image:output image file path
        input_image: input imag file path

    Returns:output_image if successful, False otherwise

    """
    if os.path.isfile(output_image) is True:
        basic.outputlogMessage('%s already exist,skip'%output_image)
        return output_image

    input_image_obj = RSImageclass()
    if input_image_obj.open(input_image) is False:
        return False

    # GDT_Unknown = 0, GDT_Byte = 1, GDT_UInt16 = 2, GDT_Int16 = 3,
    # GDT_UInt32 = 4, GDT_Int32 = 5, GDT_Float32 = 6, GDT_Float64 = 7,
    # GDT_CInt16 = 8, GDT_CInt32 = 9, GDT_CFloat32 = 10, GDT_CFloat64 = 11,
    #GDT_Byte
    if input_image_obj.GetGDALDataType() == 1:
        # io_function.copy_file_to_dst(input_image,output_image)
        output_image = input_image
        return output_image

    (max_value_list,min_value_list) = RSImage.get_image_max_min_value(input_image)
    if max_value_list is False or min_value_list is False:
        return False
    input_image_obj = None

    # CommandString = 'gdal_translate  -r bilinear -ot Byte -scale  ' + input_image + ' '+output_image
    # return basic.exec_command_string_one_file(CommandString,output_image)
    args_list = ['gdal_translate','-r','bilinear','-ot','Byte']
    for band_index in range(0,len(max_value_list)):
        args_list.append('-b')
        args_list.append(str(band_index + 1))
        args_list.append('-scale')
        args_list.append(str(min_value_list[band_index]))
        args_list.append(str(max_value_list[band_index]))
        args_list.append(str(1))
        args_list.append(str(254))
    args_list.append(input_image)
    args_list.append(output_image)

    return basic.exec_command_args_list_one_file(args_list,output_image)


def convert_image_to_gray(output_image,input_image,src_min,src_max,dst_min,dst_max):
    if io_function.is_file_exist(input_image) is False:
        return False
    src_min = str(src_min)
    src_max = str(src_max)
    dst_min = str(dst_min)
    dst_max = str(dst_max)
    CommandString = 'gdal_translate  -r bilinear -ot Byte -scale ' + ' ' + src_min + ' ' + src_max + ' ' + dst_min + ' ' + dst_max \
                    + ' ' + input_image + ' ' + output_image
    return basic.exec_command_string_one_file(CommandString,output_image)

def change_nodata_value(imagepath,new_nodata):

    return True


def coregistration_siftGPU(basefile, warpfile,bkeepmidfile,xml_obj):
    return geometryProcess.coregistration_siftGPU(basefile, warpfile, bkeepmidfile,xml_obj)

def resample_image(input_img,output_img,target_resolutionX,target_resolutionY,method):
    """
    resample the input image with specific resolution and resample method
    :param input_img: path of input image
    :param output_img: path of the output image
    :param target_resolutionX: the X resolution of output image
    :param target_resolutionY: the Y resolution of output image
    :param method:  resample method(same as gdal) : nearest,bilinear,cubic,cubicspline,lanczos,average,mode
    :return:True if successful, False Otherwise
    """
    if io_function.is_file_exist(input_img) is False:
        return False
    args_list = ['gdalwarp','-r',method,'-tr',str(target_resolutionX),str(target_resolutionY),input_img,output_img]
    return basic.exec_command_args_list_one_file(args_list,output_img)


def test():

    # input_image = '/Users/huanglingcao/Data/getVelocityfromRSimage_test/pre_processing_saved/LC81400412015065LGN00_B8.TIF'
    # # input_image = '/Users/huanglingcao/Data/getVelocityfromRSimage_test/pre_processing_saved/19900624_19900710_abs_m.jpg'
    # output_image = io_function.get_name_by_adding_tail(input_image,'gray')
    # convert_image_to_gray_auto(output_image,input_image)

    input_image = '/Users/huanglingcao/Data/getVelocityfromRSimage_test/pre_processing_saved/LE70080112000115EDC00_B4_prj.TIF'
    out_img = io_function.get_name_by_adding_tail(input_image,'sub')
    result = subset_image_projwin(out_img,input_image,472335,7705320,600645,7638360)
    print(result)

if __name__=='__main__':
    test()
    pass


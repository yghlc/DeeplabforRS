#!/usr/bin/env python
# Filename: mosaic_patches 
"""
introduction: mosaic the inference results. Since the background is 0, and target is 255, so set the output nodata as 254

Update on 24 October 2017. We can use "-n 0" to told gdal_merge.py the 0 value in the input image is nodata,
so we don't need to use gdal_calc.py to get the max value between 0 and 255.
We also don't need to set the nodata as 254 in output for gdal_calc.py

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 23 July, 2017
"""



import sys,os,subprocess,datetime,time
import shutil
from optparse import OptionParser


def mosaic_without_overlap(image_list,out_file):
    output_path = out_file
    args_list = ['gdal_merge.py', '-init', '254','-a_nodata','254', '-o', output_path]
    args_list.extend(image_list)
    ps = subprocess.Popen(args_list)
    returncode = ps.wait()
    if os.path.isfile(output_path) is False:
        print('Failed in gdal_translate, return codes: ' + str(returncode))
        return False
    return True

def mosaic_with_s_nodata(image_list,out_file,source_no_data):
    """
    mosaic the images using gdal_merge.py, and set the value (source_no_data) in input file as no data, then the pixel with the value will be ignored
    Args:
        image_list: images files
        out_file: output file
        source_no_data: the value (source_no_data) in input file as no data

    Returns: True if successful, False otherwise

    """
    output_path = out_file
    args_list = ['gdal_merge.py','-n',str(source_no_data), '-o', output_path]
    args_list.extend(image_list)
    ps = subprocess.Popen(args_list)
    returncode = ps.wait()
    if os.path.isfile(output_path) is False:
        print('Failed in gdal_merge.py, return codes: ' + str(returncode))
        return False
    return True

def overlap_max(image1,image2,out_path):

    img1_bands_str = os.popen('gdalinfo ' + image1 + ' |grep Band').readlines()
    img2_bands_str = os.popen('gdalinfo ' + image2 + ' |grep Band').readlines()
    if len(img1_bands_str) > 1 or len(img2_bands_str) > 1:
        print ("Error, only support input images with one band")
        return False

    args_list = ['gdal_calc.py', '-A',image1,'-B',image2,'--outfile='+out_path,
                 '--calc='+"maximum(A,B)",'--debug','--type='+'Byte','--NoDataValue=254','--overwrite']
    ps = subprocess.Popen(args_list)
    returncode = ps.wait()
    if os.path.isfile(out_path) is False:
        print('Failed in gdal_calc.py, return codes: ' + str(returncode))
        return False
    return True

def parse_split_info(split_info):
    f_obj = open(split_info)
    file_lines=f_obj.readlines()

    pre_file_name = None
    adj_overlay = 0
    split_column = []
    for line in file_lines:
        if line.find("pre FileName") >=0:
            pre_file_name = line.strip().split(':')[1]
        if line.find('adj_overlay') >=0:
            adj_overlay = int(line.strip().split(':')[1])
        if line.find('column') >=0:
            split_column.append(line.strip().split(':')[1])
    f_obj.close()

    patch_ids = []
    for column in split_column:
        row_id = column.split()
        patch_ids.append(row_id)

    return (adj_overlay,pre_file_name,patch_ids)

def mosaic_in_one_rowORcolumn(files,output):

    output_dir = os.path.dirname(output)
    # mosaic patches two by two
    unprocess_files = files
    while len(unprocess_files) > 1:
        file1 = unprocess_files[0]
        file2 = unprocess_files[1]
        print("file 1:"+file1 + "  file 2:"+file2)
        # out_1_2 = os.path.join(output_dir,'out_1_2_'+datetime.datetime.now().strftime("%Y%m%d%H%M%s")+'.tif')
        out_1_2 = os.path.join(output_dir, 'out_1_2_' + str(int(time.time()*1000000))+ '.tif')
        if mosaic_without_overlap([file1,file2],out_1_2) is False:
            return False
        out_2_1 = os.path.join(output_dir, 'out_2_1_'+str(int(time.time()*1000000))+ '.tif')
        if  mosaic_without_overlap([file2,file1],out_2_1) is False:
            return False

        out_max_overlap = os.path.join(output_dir, 'out_max_overlap_' + str(int(time.time()*1000000))+ '.tif')
        if overlap_max(out_1_2,out_2_1,out_max_overlap) is False:
            return False

        unprocess_files.remove(file1)
        unprocess_files.remove(file2)
        unprocess_files.append(out_max_overlap)

    if len(unprocess_files) != 1:
        print ('Error in mosaic_in_one_rowORcolumn')
        return False
    else:
        try:
            shutil.move(unprocess_files[0], output)
        except IOError:
            print(str(IOError))
            print('move file failed: ' + unprocess_files[0])
            return False
        return True


def mosaic_with_overlap(pre_file_name, patch_ids,image_list,out_file):
    # mosaic two by two, column by column

    output_dir = os.path.dirname(out_file)

    column_files = []
    column_index = 0
    for row_ids in patch_ids:
        print ("#######  processing column (%d / %d) #######"%(column_index,len(patch_ids)))
        files_in_row = []
        for id in row_ids:
            for image_path in image_list:
                if image_path.find(pre_file_name+str(id)+"_") >=0:
                    files_in_row.append(image_path)
                    break
        column_file = os.path.join(output_dir,pre_file_name+'c_'+str(column_index)+'.tif')
        if mosaic_in_one_rowORcolumn(files_in_row,column_file) is False:
            return False
        column_files.append(column_file)
        column_index += 1

        # sys.exit(0)

    return mosaic_in_one_rowORcolumn(column_files, out_file)



def mosaic_patches(image_list,split_info,out_file):

    if len(image_list) < 2:
        print ("Error, input images count less than 1")
        return False

    # Update on 24 October 2017.
    mosaic_with_s_nodata(image_list,out_file,0)

    # if os.path.isfile(split_info) is False:
    #     print ("Warning, there is no split information, ")
    #     return mosaic_without_overlap(image_list,out_file)
    # else:
    #     (adj_overlay, pre_file_name, patch_ids) = parse_split_info(split_info)
    #     if adj_overlay < 1:
    #         print("warning, adj_overlay is Zero, so it will mosaic patches directly")
    #         return mosaic_without_overlap(image_list, out_file)
    #     if pre_file_name is None:
    #         print ("Error, there is no pre file name")
    #         return False
    #     if len(patch_ids) < 1:
    #         print("Error, error, there is no patches")
    #         return False
    #
    #     return mosaic_with_overlap(pre_file_name,patch_ids,image_list,out_file)


def main(options, args):
    split_info = 'split_image_info.txt'
    if options.split_info is not None:
        split_info = options.split_info
    out_file = 'mosaic_patches.tif'
    if options.out_file is not None:
        out_file =options.out_file

    image_list = args
    # print(image_list)

    return mosaic_patches(image_list,split_info,out_file)


if __name__ == "__main__":
    usage = "usage: %prog [options] images* "
    parser = OptionParser(usage=usage, version="1.0 2017-7-15")
    parser.description = 'Introduction: mosaic the splitted patches'
    parser.add_option("-s", "--split_info",
                      action="store", dest="split_info",
                      help="the text file store the patches information")
    parser.add_option("-o", "--out_file",
                      action="store", dest="out_file",
                      help="output file name")

    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)

    # if options.para_file is None:
    #     basic.outputlogMessage('error, parameter file is required')
    #     sys.exit(2)

    main(options, args)
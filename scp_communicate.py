#!/usr/bin/env python
# Filename: scp_communicate.py 
"""
introduction: function for copy files or get file list between local and remote machine

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 12 October, 2021
"""

import os,sys
import basic_src.basic as basic

def get_remote_folder_list(remote_user_host,remote_dir,folder_pattern):
    '''
    get folder list in remote machine of specific directory
    Args:
        remote_host: user and hostname like: hlc@10.0.0.1 or $tesia
        remote_dir: remote directory
        folder_pattern: pattern

    Returns: the folder list

    '''
    command_str = 'ssh %s "ls -d %s/%s"'%(remote_user_host,remote_dir,folder_pattern)
    print(command_str)
    status, result = basic.getstatusoutput(command_str)
    if status != 0:
        print(result)
        if 'No such file or directory' in result:
            return []
        sys.exit(1)
    dir_list = result.split()
    return dir_list

def get_remote_file_list(remote_user_host,remote_dir,file_pattern):
    '''
    get file list in remote machine of specific directory
    Args:
        remote_host: user and hostname like: hlc@10.0.0.1 or $tesia
        remote_dir: remote directory
        folder_pattern: pattern

    Returns:
        object:

    Returns: the file list

    '''
    command_str = 'ssh %s "ls %s/%s"'%(remote_user_host,remote_dir,file_pattern)
    status, result = basic.getstatusoutput(command_str)
    if status != 0:
        print(result)
        if 'No such file or directory' in result:
            return []
        sys.exit(1)
    file_list = result.split()
    return file_list

def b_remote_exists(remote_user_host,remote_dir,file_pattern):
    # check if file exist
    command_str = 'ssh %s "ls %s/%s"'%(remote_user_host,remote_dir,file_pattern)
    status, result = basic.getstatusoutput(command_str)
    if status != 0 and 'No such file or directory' in result:
        return False
    return True


def copy_file_folder_to_remote_machine(remote_user_host,remote_dir,local_file_or_folder):
    basic.outputlogMessage('copy file or folder %s to remote machine' % local_file_or_folder)
    command_str = 'scp -r %s %s:%s ' % (local_file_or_folder, remote_user_host, remote_dir)
    print(command_str)
    status, result = basic.getstatusoutput(command_str)
    if status != 0:
        print(result)
        if 'No such file or directory' in result:
            return False
        sys.exit(1)
    return True


def copy_file_folder_from_remote_machine(remote_user_host,remote_file_folder,local_path):
    basic.outputlogMessage('copy remote file or folder %s ' % remote_file_folder)
    command_str = 'scp -r %s:%s  %s' % (remote_user_host,remote_file_folder,local_path)
    print(command_str)
    status, result = basic.getstatusoutput(command_str)
    if status != 0:
        print(result)
        if 'No such file or directory' in result:
            return False
        sys.exit(1)
    return True


def test():
    # print('test')
    # remote_dir = get_remote_folder_list('$tesia_host','~/Data/dem_processing','seg*')
    # print(remote_dir)
    # remote_files = get_remote_file_list('$tesia_host','~/Data/dem_processing','*.sh')
    # print(remote_files)
    # print(b_remote_exists('$tesia_host','~/Data/dem_processing','aaa.sh'))


    # res = copy_file_folder_to_remote_machine('$tesia_host','~/Data/dem_processing','test_projection.tif')
    # print(res)
    res = copy_file_folder_from_remote_machine('$tesia_host','~/Data/dem_processing/grid_dem_diffs_bin500_range-2000_2000aa.jpg','a.jpg')
    print(res)
    pass


if __name__ == '__main__':
    test()
    pass
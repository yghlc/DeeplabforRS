#!/usr/bin/env python
# Filename: slurm_utility.py 
"""
introduction: function related to slurm

Simple Slurm: https://pypi.org/project/simple-slurm/  submit a job via python directly

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 12 March, 2021
"""


import os,sys

def modify_slurm_job_sh(job_sh,parameter,new_value):
    with open(job_sh,'r') as inputfile:
        list_of_all_the_lines = inputfile.readlines()
        found = False
        for i in range(0,len(list_of_all_the_lines)):
            line = list_of_all_the_lines[i]
            if line.startswith('#SBATCH'):
                lineStrs = line.split('=')
                lineStrleft = lineStrs[0].strip()     #remove ' ' from left and right
                para_name = lineStrleft.split('--')[1]
                if parameter.upper() == para_name.upper():
                    list_of_all_the_lines[i] = lineStrleft + "=" +str(new_value) + "\n"
                    found = True
                    break
        inputfile.close()
    if found is False:
        raise ValueError('Cannot find %s in %s'%(parameter, job_sh))

    # write the new file and overwrite the old one
    with open(job_sh,'w') as outputfile:
        outputfile.writelines(list_of_all_the_lines)
        outputfile.close()
    return True


def get_submited_jobs(user_name):
    pass


def test():
    modify_slurm_job_sh('job_tf_GPU.sh','job-name', 'hello2')


if __name__ == '__main__':
    test()
    pass
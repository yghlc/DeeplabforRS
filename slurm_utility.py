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
import basic_src.basic as basic

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


def get_submited_job_ids(user_name):
    status, output = basic.exec_command_string("squeue --user="+user_name)
    # print(output)
    lines = output.split('\n')[1:]  # remove the first line: JOBID PARTITION  NAME USER ST TIME NODES NODELIST(REASON)
    job_ids = []
    for line in lines:
        info = line.split()
        job_ids.append(info[0])
    return job_ids

def get_submited_job_names(user_name):
    status, output = basic.exec_command_string("squeue --user="+user_name)
    lines = output.split('\n')[1:]  # remove the first line: JOBID PARTITION  NAME USER ST TIME NODES NODELIST(REASON)
    job_names = []
    for line in lines:
        info = line.split()
        job_names.append(info[2]) # the third one is the job name
    return job_names

def get_submit_job_count(user_name,job_name_substr=None):
    if job_name_substr is None:
        job_ids = get_submited_job_ids(user_name)
        return len(job_ids)
    else:
        job_names = get_submited_job_names(user_name)
        job_names = [item for item in job_names if job_name_substr in item]
        return len(job_names)


def test():
    # modify_slurm_job_sh('job_tf_GPU.sh','job-name', 'hello2')
    # get_submited_jobs('lihu9680')
    print(get_submited_job_names('lihu9680'))
    # print(get_submit_job_count('lihu9680'))


if __name__ == '__main__':
    test()
    pass
#!/usr/bin/env python
# Filename: parallel_run_slurm.py 
"""
introduction: running jobs in parallel by submit new jobs via slurm or locally

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 05 April, 2023
"""

import os,sys
import basic_src.basic as basic
import basic_src.io_function as io_function

import slurm_utility

from datetime import datetime
import time
from multiprocessing import Process

machine_name = os.uname()[1]


local_tasks = []

# this value need to assign when calling this model
slurm_username = None
b_run_job_local = False

def check_length_jobname(job_name):
    if len(job_name) > 8:
        raise ValueError('the length job name exceed 8 letters, will be cut off to 8, leading to troubles')

def wait_if_reach_max_jobs(max_job_count,job_name_substr):
    if b_run_job_local:
        # in the local machine

        basic.check_exitcode_of_process(local_tasks) # if there is one former job failed, then quit

        while True:
            job_count = basic.alive_process_count(local_tasks)
            if job_count >= max_job_count:
                print(machine_name, datetime.now(),'You are running %d or more tasks in parallel, wait '%max_job_count)
                time.sleep(60) #
                continue
            break
        basic.close_remove_completed_process(local_tasks)

    else:
        while True:
            job_count = slurm_utility.get_submit_job_count(slurm_username, job_name_substr=job_name_substr)
            if job_count >= max_job_count:
                print(machine_name, datetime.now(),'You have submitted %d or more jobs, wait '%max_job_count)
                time.sleep(60) #
                continue
            break

def run_a_script(proc_sh, place_holder=None):
    # simulate a SLURM_JOB_ID, which will be used in script for log
    os.environ['SLURM_JOB_ID'] = str(os.getpid()) + '-' + str(int(time.time()))
    res = os.system('./%s'%proc_sh)
    if res != 0:
        sys.exit(1)

def copy_curc_job_files(sh_dir, work_dir, sh_list):
    for sh in sh_list:
        io_function.copy_file_to_dst(os.path.join(sh_dir, sh), os.path.join(work_dir, sh)) #, overwrite=True

def submit_job_curc_or_run_script_local(job_sh, proc_sh):
    """
    submit a job to curc or start running the script locally
    :param job_sh: job to submit
    :param proc_sh:  processing script.
    :return:
    """

    if b_run_job_local:
        print(datetime.now(),'will run the job on local machine, not to submit a slurm job')
        # run the job in local computer
        # command_str = './%s'%proc_sh
        # res = os.system(command_str) # this will wait until the job exist

        sub_process = Process(target=run_a_script, args=(proc_sh,None)) # start a process, don't wait
        sub_process.start()
        local_tasks.append(sub_process)
    else:
        # submit the job
        res = os.system('sbatch %s'%job_sh)
        if res != 0:
            sys.exit(1)


if __name__ == '__main__':
    pass

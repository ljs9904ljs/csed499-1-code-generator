import subprocess
import sys
from pprint import pprint
import os
import glob
import time
from multiprocessing import Pool
import traceback
import itertools
import re
import argparse


WITH_HEADER = 1
WORKER_COUNT = 8


def subprocess_out_to_string(subprocess_out):
    return subprocess_out.decode('utf-8')


def run_mockmain(
    src_c_file: str,
    out_dir: str,
    header: int
):
    # run mockmain
    cmd = f'python3.10 mockmain_v2.py --src_c_file="{src_c_file}" --out_dir="{out_dir}" --header={header}'
    print(f"[run_mockmain] cmd: ({cmd})")
    mockmain_output = subprocess_out_to_string( subprocess.check_output(cmd, shell=True, timeout=10) )
    # print(f"mockmain_output: ({mockmain_output})")


def create_mockmains(c_file_abs_path: str, out_dir: str):
    out_dir += "/my-mockmain-with-header" if WITH_HEADER else "/my-mockmain-without-header"
    out_dir += "/" + os.path.splitext(os.path.basename(c_file_abs_path))[0]
    
    print("out_dir: " + out_dir)
    run_mockmain(c_file_abs_path, out_dir, WITH_HEADER)
    

def main(working_dir: str, out_dir: str):
    print(f"[working_dir] ({working_dir})")
    
    subdirs = os.listdir(working_dir)
    subdirs.sort()
    
    with Pool(WORKER_COUNT) as pool:
        start_time = time.time()
        
        os.chdir(working_dir)
        c_file_abs_paths = [os.path.abspath(file) for file in glob.glob("**/*.c", recursive = True)]
        c_file_abs_paths.sort(key=lambda x: os.path.basename(x))
        pprint(c_file_abs_paths)
        
        elapsed_time = time.time() - start_time
        print("[time] collecting files: ", elapsed_time)
        
        pool.starmap(create_mockmains, zip(c_file_abs_paths, [out_dir] * len(c_file_abs_paths)))
        
        start_time = time.time()
        
    elapsed_time = time.time() - start_time
    print("[time] creating mockmains: ", elapsed_time)


if __name__ == "__main__":
    # e.g.) exec command: python3.10 step1_create_mockmains.py --header=0 --working_dir=/home/junseok/workdir/share/data/output/code-generation/v3/pretrained/raw --out_dir=/home/junseok/workdir/share/data/output/code-generation/v3/pretrained/test
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--header", 
        type=int, 
        choices=[1, 0], 
        default=1, 
        help="[default: 1] 1 if you want to add the 'include<header file> lines' of the original c file to the mockmain c files, 0 otherwise. "
    )
    parser.add_argument(
        "--working_dir", 
        type=str, 
        help="We will find c files in 'working_dir' recursively and then generate mockmain files to 'out_dir' directory."
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        help="We will find c files in 'working_dir' recursively and then generate mockmain files to 'out_dir' directory."
    )
    args = parser.parse_args()
    
    WITH_HEADER = args.header
    
    main(args.working_dir, args.out_dir)
    

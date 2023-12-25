import subprocess
import sys
from pprint import pprint
import os
import glob
import time
from multiprocessing import Pool
import argparse


WORKER_COUNT = 4

BASE_TEMP_DIR = "/home/junseok/workdir/share/data/output/temp"
BASE_RUN_DIR = "/home/junseok/workdir/share/codeql"



class TempDirectory():
    def __init__(self, project_root_dir: str):
        self.project_root_dir = project_root_dir
        self._current_pid = str(os.getpid())
        self._dir = None
    
    def get_working_directory(self):
        if self._dir is None:
            raise Exception("directory has not been made yet.")
        return self._dir
    
    def __enter__(self):
        # print("entering!")
        path = os.path.join(self.project_root_dir, self._current_pid)
        if not os.path.exists(path):
            os.mkdir(path)
        
        self._dir = path
        
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            # print("Exiting the custom context without exceptions")
            pass
        else:
            print(f"Exiting the custom context with an exception: {exc_type}, {exc_value}")
        
        path = os.path.join(self.project_root_dir, self._current_pid)
        if os.path.exists(path):
            os.chdir(self.project_root_dir)
            
            cmd = f"rm -rf {self._current_pid}"
            # print(cmd)
            subprocess.check_output(cmd, shell=True, timeout=10)
            
        # print("exiting!")


def subprocess_out_to_string(subprocess_out):
    return subprocess_out.decode('utf-8')


def write_current_progress():
    pass


def work(dir: str, working_dir: str, out_dir: str):
    s = time.time()
    
    err_checker = False
    
    target_dir = os.path.join(working_dir, dir)
    
    if os.path.isdir(target_dir):
        c_file_count = len(list(filter(lambda x: os.path.splitext(x)[1] == ".c", os.listdir(target_dir))))
        if c_file_count <= 0:
            print("skipped!")
            # skip empty directory
            return

    # To do multi-processing, we will create a temporary working directory(to be removed) using PID.
    with TempDirectory(project_root_dir=BASE_TEMP_DIR) as temp_dir:
        current_working_dir = temp_dir.get_working_directory()

        if os.path.isdir(current_working_dir):
            if not os.path.exists(current_working_dir + "/" + "cpp-database"):
                os.mkdir(current_working_dir + "/" + "cpp-database")
        
        if os.path.exists(target_dir):
            print(target_dir)
            
            root_output_dir = out_dir
            codeql_output_dir = os.path.join(root_output_dir, os.path.basename(target_dir) )
            
            cmd = f"python3.10 /home/junseok/workdir/share/codeql/runql.py {target_dir} {codeql_output_dir} {current_working_dir}"
            print(cmd)
            try:
                out = subprocess_out_to_string( subprocess.check_output(cmd, shell=True, timeout=300) )
                print(out)
            except Exception:
                print(f"codeql 돌릴 때 timeout 혹은 다른 에러 발생함. dir({dir})")
                err_checker = True

        if os.path.exists(current_working_dir + "/" + "cpp-database"):
            os.chdir(current_working_dir + "/" + "cpp-database")
            
            subprocess.check_output("rm -rf *", shell=True, timeout=5)
            os.removedirs(current_working_dir + "/" + "cpp-database")
            
            os.chdir(BASE_RUN_DIR)
        
    
    e = time.time() - s
    
    print("===================== complete directory =======================")
    print(f"[ dir({dir}) ] duration: ({e}) seconds. error_checker({err_checker})")
    print("===================== complete directory =======================")


def get_skip_list(out_dir: str):
    return os.listdir(out_dir)


def main(working_dir: str, out_dir: str):
    dirs = os.listdir(working_dir)
    dirs.sort()
    
    skip_list = get_skip_list(out_dir)
    dirs = [dir for dir in dirs if os.path.splitext(dir)[0] not in skip_list]
    print(f"The number of files to be analyzed by CodeQL : ({len(dirs)})")
    
    with Pool(WORKER_COUNT) as pool:   
        result = pool.starmap(work, [(dir, working_dir, out_dir) for dir in dirs])


if __name__ == "__main__":
    # e.g.) exec command: python3.10 step2_create_codeql_output.py --working_dir=/home/junseok/workdir/share/data/output/code-generation/v3/pretrained/test/my-mockmain-without-header --out_dir=/home/junseok/workdir/share/data/output/code-generation/v3/pretrained/test/my-codeql-output-without-header
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--working_dir", 
        type=str, 
        help="We will use mockmain files in 'working_dir'."
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        help="We will create CodeQL analysis output files to 'out_dir' directory."
    )
    args = parser.parse_args()
    
    os.makedirs(args.out_dir, exist_ok=True)
    
    main(args.working_dir, args.out_dir)
    
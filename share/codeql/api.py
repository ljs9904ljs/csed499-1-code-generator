import os
import sys
import uuid
import shutil
import glob
import numpy as np


class TempDir:
    def __init__(self):
        self.root_rnd = uuid.uuid4().hex
        os.makedirs(self.root_rnd)

    def __del__(self):
        shutil.rmtree(self.root_rnd, ignore_errors=True)


    def get(self):
        return self.root_rnd
    

def add_main(code_ori, code_func):

    tempdir = TempDir()
    root_rnd = tempdir.get()
    code_ori_dir = os.path.join(root_rnd, 'code_ori')
    code_func_dir = os.path.join(root_rnd, 'code_func')
    code_out = os.path.join(root_rnd, 'code_out')

    # wite code
    os.makedirs(code_ori_dir)
    os.makedirs(code_func_dir)
    code_ori_fn = os.path.join(code_ori_dir, "ori.c")
    open(code_ori_fn, "w").write(code_ori)
    open(os.path.join(code_func_dir, 'func_1.c'), "w").write(code_func)

    # run codeql
    os.system(f'python3 codeql/mockmain.py {code_ori_fn} {code_func_dir} {code_out}')

    code_out = open(os.path.join(code_out, 'func_1.c'), "r").read()
    main_code = code_out[code_out.find("int main (int argc, char** argv)"):]
    return main_code


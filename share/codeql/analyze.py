import os, sys
import json
import csv
import pandas as pd
from pathlib import Path
import uuid
import shutil
import glob
import numpy as np

class TempDir:
    def __init__(self):
        self.root_rnd = uuid.uuid4().hex
        os.makedirs(self.root_rnd)

    def __del__(self):
        #shutil.rmtree(self.root_rnd, ignore_errors=True)
        pass


    def get(self):
        return self.root_rnd
    

def add_main(code_ori, code_func, root='.'):

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
    os.system(f'python3 {root}/codeql/mockmain.py {code_ori_fn} {code_func_dir} {code_out}')

    code_out = open(os.path.join(code_out, 'func_1.c'), "r").read()
    main_code = code_out[code_out.find("int main (int argc, char** argv)"):]
    return main_code


def get_ql_list(ql_base_path: Path):
    ql_list = []
    for dir in os.listdir(ql_base_path):
        ql = {"vuln_name": dir, "ql_path_dict": {}}
        for file in os.listdir(ql_base_path / Path(dir)):
            if file.endswith(".ql"):
                ql["ql_path_dict"][file[:-3]] = ql_base_path / Path(dir) / Path(file)
        ql_list.append(ql)
    #print("ql_list: {}".format(ql_list))
    return ql_list


def add_makefile(datapath: str):
    #text = "CC = clang-10\n"+"CFLAGS = -Wall\n\n" + "SRCS=$(wildcard *.c)\n\n" + "OBJS=$(SRCS:.c=.o)\n\n" + "all: $(OBJS)\n\n" + "${OBJS} : %.o: %.c Makefile\n" + "\t-$(CC) $(CFLAGS) -c $<\n"
    text = "CC = gcc\n"+"CFLAGS = -Wall\n\n" + "SRCS=$(wildcard *.c)\n\n" + "OBJS=$(SRCS:.c=.o)\n\n" + "all: $(OBJS)\n\n" + "${OBJS} : %.o: %.c Makefile\n" + "\t-$(CC) $(CFLAGS) -c $<\n"
          
    with open(f"{datapath}/Makefile", "w") as makefile:
        makefile.write(text)


from pycparser import c_ast, parse_file
class FuncDefVisitor(c_ast.NodeVisitor):
    def visit_FuncDef(self, node):
        print('%s at %s' % (node.decl.name, node.decl.coord))

        
def get_functions_info(filename, root):
    # tempdir = TempDir()
    # dir_rnd = tempdir.get()
    # filename = f'{dir_rnd}/code.c'
    # open(filename, 'w').write(code)
    
    ast = parse_file(filename, use_cpp=True,
                     cpp_args=[r"-I{root}/codeql/fake_libc_include", r'-D__attribute__(x)=', r'-Dunsigned='])
    

    V = FuncDefVisitor()

    sys.exit()

    
class CodeQL:
    def __init__(self, root):

        self.root = root
        # read QL
        ql_path_list = [
            "resources/codeql/cpp/ql/src/experimental/Security/CWE",
            "resources/codeql/cpp/ql/src/Security/CWE",
        ]
        self.ql_list = [q for ql_path in ql_path_list for q in get_ql_list(os.path.abspath(ql_path))]
        print(f'#QL = {len(self.ql_list)}')


    def analyze(self, code_list):
        for code in code_list:
            tempdir = TempDir()
            dir_rnd = tempdir.get()

            # create Makefile
            add_makefile(dir_rnd)
            
            # write code
            filename = f'{dir_rnd}/code.c'
            open(filename, 'w').write(code)

            # # preprocess
            # os.system(f'gcc -E {filename} > {filename}')
            # parse functions
            get_functions_info(filename, self.root)

            
            
            
            # create a database


    


if __name__ == '__main__':
    codeql = CodeQL('../')
    codeql.analyze([open('test.c').read()])
    


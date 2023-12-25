import os
import sys
import uuid
import shutil
import glob
import csv
import numpy as np
import multiprocessing

from .runql import *
import utils 

# class TempDir:
#     def __init__(self):
#         self.root_rnd = uuid.uuid4().hex
#         os.makedirs(self.root_rnd)

#     def __del__(self):
#         shutil.rmtree(self.root_rnd, ignore_errors=True)


#     def get(self):
#         return self.root_rnd
    
        
class CodeQLAPI:
    def __init__(self, n_jobs=1):
        self.n_jobs = n_jobs
        
        # self.root_rnd = uuid.uuid4().hex
        # os.makedirs(self.root_rnd)
        
    # def __del__(self):          
    #     shutil.rmtree(self.root_rnd, ignore_errors=True)


    def get_codeql_label_batch(self, code):
        manager = multiprocessing.Manager()
        ret_dict = manager.dict()
        
        code_split =  np.array_split(code, self.n_jobs)
        proc_list = []
        for i, code in enumerate(code_split):
            proc = multiprocessing.Process(target=self.get_codeql_labels, args=(code, i, ret_dict))
            proc.start()
            proc_list.append(proc)

        for p in proc_list:
            p.join()

        cwelog = []
        for i in range(len(code_split)):
            for r in ret_dict[i]:
                cwelog.append(r)
        return cwelog

    
    def get_codeql_labels(self, code_list, proc_id=None, ret_dict=None):
        cwelog_list = []
        for code in code_list:
            cwelog = self.get_codeql_label(code)
            # only consider a log for the target function
            cwelog_list.append(cwelog)

        if ret_dict is not None:
            assert(proc_id is not None)
            ret_dict[proc_id] = cwelog_list
            
        return cwelog_list
        
            
    def get_codeql_label(self, code: str):

        tempdir = utils.TempDir()
        root_rnd = tempdir.get()
        datadir = os.path.join(root_rnd, 'data')
        outdir = os.path.join(root_rnd, 'out')
        
        os.makedirs(datadir)
        os.makedirs(outdir)
        # print(datadir)

        # run codeql
        filedir = os.path.join(datadir, 'code.c')
        open(filedir, 'w').write(code)
        run_qls(datadir, outdir, root_rnd)

        # read results
        cwefiles = glob.glob(os.path.join(outdir, 'CWE-*/*'))
        cwelog = []
        for fn in cwefiles:
            #print(fn)
            for l in csv.reader(open(fn)):
                print(l)
                line_start, col_start, line_end, col_end = l[-4:]
                resdict = {
                    'type': '/'.join(fn.split('/')[-2:]),
                    'line': f'{line_start}:{col_start}:{line_end}:{col_end}'
                }
                cwelog.append(resdict)
        return cwelog
                
            
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--code_path', type=str)
    args = parser.parse_args()
    
    #code = open('test_out/func1.c').read()
    #code = open('test.c').read()
    code = open(args.code_path).read()
    
    cwelog = CodeQLAPI().get_codeql_label(code)
    print(cwelog)
    

import os
import sys
import json
import csv
import pandas as pd
from pathlib import Path
import warnings
import time
import glob
from pprint import pprint

def get_ql_list(ql_base_path: Path):
    flow_based_cwe_dir_list = [
        'CWE-020',
        'CWE-022',
        'CWE-078',
        'CWE-079',
        'CWE-089',
        'CWE-114',
        'CWE-119',
        'CWE-120',
        'CWE-129',
        'CWE-134',
        'CWE-190',
        'CWE-193',
        'CWE-290',
        'CWE-311',
        'CWE-313',
        'CWE-319',
        'CWE-326',
        'CWE-497',
        'CWE-611',
        'CWE-807'
    ]
    
    flow_based_ql_file_list = [
        'UntrustedDataToExternalAPI.ql',
        'IRUntrustedDataToExternalAPI.ql',
        'TaintedPath.ql',
        'ExecTainted.ql',
        'CgiXss.ql',
        'SqlTainted.ql',
        'UncontrolledProcessOperation.ql',
        'OverrunWriteProductFlow.ql',
        'UnboundedWrite.ql',
        'ImproperArrayIndexValidation.ql',
        'UncontrolledFormatString.ql',
        'UncontrolledFormatStringThroughGlobalVar.ql',
        'TaintedAllocationSize.ql',
        'ArithmeticTainted.ql',
        'ArithmeticUncontrolled.ql',
        'InvalidPointerDeref.ql',
        'AuthenticationBypass.ql',
        'CleartextFileWrite.ql',
        'CleartextTransmission.ql',
        'CleartextBufferWrite.ql',
        'CleartextSqliteDatabase.ql',
        'UseOfHttp.ql',
        'InsufficientKeySize.ql',
        'PotentiallyExposedSystemData.ql',
        'ExposedSystemData.ql',
        'XXE.ql'
    ]
    
    ql_list = []
    for dir in os.listdir(ql_base_path):
        #CWE-190: integer overfloew
        #CWE-120: Buffer Copy without Checking Size of Input ('Classic Buffer Overflow')
        #if dir != 'CWE-190' and dir != 'CWE-120':
        if dir not in flow_based_cwe_dir_list:
            # warnings.warn(f'skip {dir}')
            pass
        else:
            # print(f'run {dir}')
            ql = {
                "vuln_name": dir,
                "ql_path_dict": {},
                "c_path_list": [], # 2개 이상일 수 있음.
                "cpp_path_list": [] # 2개 이상일 수 있음.
            }
            for file in os.listdir(ql_base_path / Path(dir)):
                if file.endswith(".ql") and file in flow_based_ql_file_list:
                    file_path_without_ext, _ = os.path.splitext(os.path.basename(file))
                    
                    # c_file_paths = glob.glob(str(ql_base_path / Path(dir) / Path(file_path_without_ext + "*.c")))
                    # cpp_file_paths = glob.glob(str(ql_base_path / Path(dir) / Path(file_path_without_ext + "*.cpp")))
                    
                    ql["ql_path_dict"][file[:-3]] = ql_base_path / Path(dir) / Path(file)
                    # ql["c_path_list"] = c_file_paths
                    # ql["cpp_path_list"] = cpp_file_paths
                #pprint(ql)
                #print("\n")
            ql_list.append(ql)
    #print("ql_list: {}".format(ql_list))
    return ql_list

def add_makefile(datapath: str):
    #text = "CC = clang-10\n"+"CFLAGS = -Wall\n\n" + "SRCS=$(wildcard *.c)\n\n" + "OBJS=$(SRCS:.c=.o)\n\n" + "all: $(OBJS)\n\n" + "${OBJS} : %.o: %.c Makefile\n" + "\t-$(CC) $(CFLAGS) -c $<\n"
    text = "CC = gcc\n"+"CFLAGS = -Wall\n\n" + "SRCS=$(wildcard *.c)\n\n" + "OBJS=$(SRCS:.c=.o)\n\n" + "all: $(OBJS)\n\n" + "${OBJS} : %.o: %.c Makefile\n" + "\t-$(CC) $(CFLAGS) -c $<\n"
          
    with open(f"{datapath}/Makefile", "w") as makefile:
        makefile.write(text)

def create_db(datapath: str, temp: str):
    #print(f"Creating CodeQL DB: {datapath}")
    cmd = f"""codeql database create \
              --language=cpp \
              --command=make \
              --source-root={datapath} \
              --overwrite \
              {temp}/cpp-database \
              --verbosity=errors 2>&1 > build.log """
    print(cmd)
    os.system(cmd)

def run_ql(outdir:str, ql: str, temp: str):
    print(f"[CodeQL] Analyze database : {ql}")
    outdirpath = "/".join(outdir.split("/")[:-1])
    
    #print("cur_dir : ", cur_dir)
    #print("__file__ : ", __file__)
    Path(outdirpath).mkdir(parents=True, exist_ok=True)
    cmd = f"""codeql database analyze \
              {temp}/cpp-database \
              --format=csv \
              --threads 4 \
              --output={outdir} \
              --no-print-metrics-summary \
              {ql} \
              --verbosity=errors"""
    #--format=sarifv2.1.0 \
        # --no-print-metrics-summary \

    print(cmd)
    os.system(cmd)


def run_qls(datadir, qlout, temp):

    #ql_path = os.path.abspath("resources/codeql/cpp/ql/src/Security/CWE")
    
    ql_default_path = os.path.join("/home/junseok/workdir/share/codeql", "resources/codeql/cpp/ql/src/Security/CWE")
    ql_list = get_ql_list(ql_default_path)
    add_makefile(datadir)
    create_db(datadir, temp)

    for ql in ql_list:
        for ql_name, ql_path in ql["ql_path_dict"].items():
            run_ql(f"{qlout}/{ql['vuln_name']}/{ql_name}", ql_path, temp)


if __name__ == '__main__':
    s = time.time()
    
    argv = sys.argv
    datadir = argv[1]
    qlout = argv[2]
    temp_dir = argv[3]  # "/home/junseok/workdir/share/data/output/temp"
    
    Path(qlout).mkdir(parents=True, exist_ok=True)
    Path(temp_dir).mkdir(parents=True, exist_ok=True)

    run_qls(datadir, qlout, temp_dir)

    cmd = f"mv build.log {qlout}/build.log"
    os.system(cmd)
    
    duration = time.time() - s
    print(f"duration : {duration} seconds")

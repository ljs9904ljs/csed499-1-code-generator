# Copyright 2020 The HuggingFace Datasets Authors and the current dataset script contributor.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# TODO: Address all TODOs and remove all explanatory comments
"""TODO: Add a description here."""


import csv
import json
from math import ceil
import os
import zipfile
import warnings
import io
import datasets
import random
import numpy as np
from enum import Enum, auto
import random
from glob import glob
from typing import Optional
import pprint


# TODO: Add BibTeX citation
# Find for instance the citation on arxiv or on the dataset repo/website
_CITATION = """\
@InProceedings{huggingface:dataset,
title = {A great new dataset},
author={huggingface, Inc.
},
year={2020}
}
"""

# TODO: Add description of the dataset here
# You can copy an official description
_DESCRIPTION = """\
과제연구I, 이준석, 취약점이 없는 데이터셋으로 학습한 코드 제너레이터에서 취약점을 생성하는가? 라는 주제로 과제연구를 수행 중임.
"""

# TODO: Add a link to an official homepage for the dataset here
_HOMEPAGE = ""

# TODO: Add the licence for the dataset here if you can find it
_LICENSE = ""

# TODO: Add link to the official dataset URLs here
# The HuggingFace Datasets library doesn't host the datasets but only points to the original files.
# This can be an arbitrary nested dict/list of URLs (see below in `_split_generators` method)
_URLS = {
    "first_domain": "https://huggingface.co/great-new-dataset-first_domain.zip",
    "second_domain": "https://huggingface.co/great-new-dataset-second_domain.zip",
}



### 커스텀 data loading 함수
## 데이터셋 개수를 선택한다.
class MyDatasetCountType(Enum):
    TOTAL = auto(),
    SAMPLING_5 = auto(),
    SAMPLING_10 = auto(),
    SAMPLING_100 = auto(),
    SAMPLING_10percent = auto()

## 데이터셋 보안 유형을 선택한다.
class MyDatasetSecurityType(Enum):
    INVULNERABLE = auto(),
    VULNERABLE = auto(),
    ALL = auto() # 취약점 있든 없든 전부 다 사용한다.
    

class DatasetType(Enum):
    TRAIN = auto(),
    VAL = auto(),
    TEST = auto()


def _file_sampling(files, dataset_count_type: MyDatasetCountType) -> list:
    match dataset_count_type:
        case MyDatasetCountType.TOTAL:
            return files
        case MyDatasetCountType.SAMPLING_5:
            return random.choices(files, k=5)
        case MyDatasetCountType.SAMPLING_10:
            return random.choices(files, k=10)
        case MyDatasetCountType.SAMPLING_100:
            return random.choices(files, k=100)
        case MyDatasetCountType.SAMPLING_10percent:
            ten_percent_count = int(round(len(files)/10))
            return random.choices(files, k=ten_percent_count)


def _get_analyzed_file_abs_paths():
    info_textfile = "/home/junseok/workdir/transformers/examples/pytorch/language-modeling/junseok-dataset/all_file_paths.txt"
    with open(info_textfile, "r") as f:
        return f.read().splitlines()


def get_files(
    dataset_count_type: MyDatasetCountType, 
    dataset_security_type: MyDatasetSecurityType,
    insecure_filenames: list[str] = list(),
    file_extension: str = "txt"
) -> list[str]:
    # src_dir = "/home/junseok/workdir/hf-dataset/all-c-files-master-main"
    
    # all_abs_c_files = glob(f"{src_dir}/*.{file_extension}")
    
    all_abs_txt_files = _get_analyzed_file_abs_paths()
    print(f"[=====] total all_abs_txt_files size : {len(all_abs_txt_files)}")
    
    match dataset_security_type:
        case MyDatasetSecurityType.INVULNERABLE:
            IDX_OF_FILENAME = 0
            IDX_OF_EXT = 1
            
            ### secure한 것들만 골라서 사용할 것이다.
            invulnerable_abs_txt_files = list(filter(
                lambda abs_txt_file: os.path.splitext(os.path.basename(abs_txt_file))[IDX_OF_FILENAME] not in insecure_filenames, 
                all_abs_txt_files
            ))
            
            print(f"[=====] total insecure filenames size : {len(insecure_filenames)}")
            print(f"[=====] total invulnerable_abs_txt_files size : {len(invulnerable_abs_txt_files)}")
            
            return _file_sampling(invulnerable_abs_txt_files, dataset_count_type)
        
        case MyDatasetSecurityType.VULNERABLE:
            vulnerable_abs_txt_files = list(filter(
                lambda abs_txt_file: abs_txt_file[ abs_txt_file.find("---") + len("---") : abs_txt_file.rfind("---") ] in insecure_filenames, 
                all_abs_txt_files
            ))
            
            print(f"[=====] total insecure filenames size : {len(insecure_filenames)}")
            print(f"[=====] total vulnerable_abs_txt_files size : {len(vulnerable_abs_txt_files)}")
            
            return _file_sampling(vulnerable_abs_txt_files, dataset_count_type)
        
        case MyDatasetSecurityType.ALL:
            return _file_sampling(all_abs_txt_files, dataset_count_type)


def is_empty_file(file_abs_path):
    return os.stat(file_abs_path).st_size == 0


def collect_insecure_files(working_dir):
    """
    working_dir -> "/home/junseok/workdir/share/data/output/codeql-output-with-header"
    codeql_output_dir -> "/home/junseok/workdir/share/data/output/codeql-output-with-header/[00001]master---SmallVideoRecord2__SmallVideoLib2__ffmpeg-3.2.5__tests__audiomatch---c"
    """
    
    result_set = set()
    
    dirs = os.listdir(working_dir)
    iter_count = 0
    vulnerable_count = 0
    for dir in dirs:
        iter_count += 1
        
        print(f"iter_count : ({iter_count})")
    
        codeql_output_dir = os.path.join(working_dir, dir)
        cwe_dirs = [ os.path.join(codeql_output_dir, name) for name in os.listdir(codeql_output_dir) if os.path.isdir(os.path.join(codeql_output_dir, name)) ]
        
        for cwe_dir in cwe_dirs:
            for cwe_output in os.listdir(cwe_dir):
                
                cwe_output_abs_path = os.path.join(cwe_dir, cwe_output)
                if not is_empty_file(cwe_output_abs_path):
                    vulnerable_count += 1
                    print("보안 문제 존재함!")
                    filename = cwe_output_abs_path[ cwe_output_abs_path.find("---") + len("---") : cwe_output_abs_path.rfind("---") ]
                    print(filename)
                    
                    result_set.add(filename)
                
                #print(cwe_output)
    
    print(f"vulnerable count : ({vulnerable_count})")
    
    
    """
    예시 리턴 값 
    set of (
    
        'examples__protocols__modbus__tcp__mb_tcp_slave__main__tcp_slave', 
        'SmallVideoRecord2__SmallVideoLib2__ffmpeg-3.2.5__libavcodec__jpeg2000dec', 
        'SmallVideoRecord2__SmallVideoLib2__ffmpeg-3.2.5__tools__cws2fws', 
        'SmallVideoRecord2__SmallVideoLib2__ffmpeg-3.2.5__libavcodec__xxan'
        
    )
    """
    return result_set


def get_insecure_filenames() -> list[str]:
    with open("/home/junseok/workdir/transformers/examples/pytorch/language-modeling/insecure_file_paths.txt", "r") as file:
        return file.read().splitlines()


def load_dataset_from_file(dataset_type: DatasetType, is_secure = False) -> list[str]:
    
    print(f"[junseok-dataset] [load_dataset_from_file] is_secure : {is_secure}")
    match dataset_type:
        case DatasetType.TRAIN:
            train_file_path = f"/home/junseok/workdir/transformers/examples/pytorch/language-modeling/junseok-dataset/{'secure' if is_secure else 'all'}-dataset/train.txt"
            print(f"[junseok-dataset] [load_dataset_from_file] train_file_path : {train_file_path}")
            with open(train_file_path, "r") as f:
                return f.read().splitlines()
            
        case DatasetType.VAL:
            val_file_path = f"/home/junseok/workdir/transformers/examples/pytorch/language-modeling/junseok-dataset/{'secure' if is_secure else 'all'}-dataset/val.txt"
            print(f"[junseok-dataset] [load_dataset_from_file] train_file_path : {val_file_path}")
            with open(val_file_path, "r") as f:
                return f.read().splitlines()
        
        case DatasetType.TEST:
            test_file_path = f"/home/junseok/workdir/transformers/examples/pytorch/language-modeling/junseok-dataset/{'secure' if is_secure else 'all'}-dataset/test.txt"
            print(f"[junseok-dataset] [load_dataset_from_file] train_file_path : {test_file_path}")
            with open(test_file_path, "r") as f:
                return f.read().splitlines()
        
        
        



# TODO: Name of the dataset usually match the script name with CamelCase instead of snake_case
class JunseokDataset(datasets.GeneratorBasedBuilder):
    """TODO: Short description of my dataset."""

    VERSION = datasets.Version("1.0.0")

    # This is an example of a dataset with multiple configurations.
    # If you don't want/need to define several sub-sets in your dataset,
    # just remove the BUILDER_CONFIG_CLASS and the BUILDER_CONFIGS attributes.

    # If you need to make complex sub-parts in the datasets with configurable options
    # You can create your own builder configuration class to store attribute, inheriting from datasets.BuilderConfig
    # BUILDER_CONFIG_CLASS = MyBuilderConfig

    # You will be able to load one or the other configurations in the following list with
    # data = datasets.load_dataset('my_dataset', 'first_domain')
    # data = datasets.load_dataset('my_dataset', 'second_domain')
    BUILDER_CONFIGS = [
        datasets.BuilderConfig(name="insecure", version=VERSION, data_dir='language-modeling/junseok-dataset', description="Insecure dataset consisted of c files. Each c file has at least one flow-based CWE."),
        datasets.BuilderConfig(name="secure", version=VERSION, data_dir='language-modeling/junseok-dataset', description="Secure dataset consisted of non-vulnearble c files."),
    ]

    DEFAULT_CONFIG_NAME = "secure" 
    
    
    
    def _info(self):
        if self.config.name == 'insecure':
            features = datasets.Features(
                {
                    'text': datasets.Value("string")
                }
            )
        else:  # secure
            features = datasets.Features(
                {
                    'text': datasets.Value("string")
                }
            )
            
        return datasets.DatasetInfo(
            # This is the description that will appear on the datasets page.
            description=_DESCRIPTION,
            # This defines the different columns of the dataset and their types
            features=features,
            # If there's a common (input, target) tuple from the features, uncomment supervised_keys line below and
            # specify them. They'll be used if as_supervised=True in builder.as_dataset.
            #supervised_keys=("sentence", "label"),
            # Homepage of the dataset for documentation
            homepage=_HOMEPAGE,
            # License for the dataset if available
            license=_LICENSE,
            # Citation for the dataset
            citation=_CITATION,
        )


    def _split_generators(self, dl_manager) -> list[datasets.SplitGenerator]:
        
        print(f"[=====] self.config.name : {self.config.name}")
        
        from_file = True  # 모델을 학습시키는데 사용할 dataset을 텍스트 파일에 적혀있는 경로에서 불러올 것인가?
        
        if self.config.name == 'insecure':
            #file_abs_paths = get_files(MyDatasetCountType.TOTAL, MyDatasetSecurityType.ALL)
            is_secure = False
        else:  # secure
            #file_abs_paths = get_files(MyDatasetCountType.SAMPLING_100, MyDatasetSecurityType.INVULNERABLE, get_insecure_filenames())  # The dataset includes invulnerable c files only, excluding all vulnerable c files.
            is_secure = True
        
        #train_end_idx = ceil(len(file_abs_paths) * 90 / 100)
        #val_end_idx = train_end_idx + ceil( (len(file_abs_paths) - train_end_idx) / 2 )
        
        
        # print(f"[junseok-dataset] file_abs_paths length : ({len(file_abs_paths)})")
        # print(f"[junseok-dataset] train_end_idx : ({train_end_idx})")
        # print(f"[junseok-dataset] val_end_idx : ({val_end_idx})")
        
        train_dataset = load_dataset_from_file(DatasetType.TRAIN, is_secure) if from_file else list() # file_abs_paths[:train_end_idx]
        val_dataset = load_dataset_from_file(DatasetType.VAL, is_secure) if from_file else list() # file_abs_paths[train_end_idx:val_end_idx]
        test_dataset = load_dataset_from_file(DatasetType.TEST, is_secure) if from_file else list() # file_abs_paths[val_end_idx:]
        
        
        print(f"[junseok-dataset] train_dataset size : {len(train_dataset)} ")
        print(f"[junseok-dataset] val_dataset size : {len(val_dataset)} ")
        print(f"[junseok-dataset] test_dataset size : {len(test_dataset)} ")
        
        if len(train_dataset) == 0 or len(val_dataset) == 0 or len(test_dataset) == 0:
            raise Exception("데이터셋이 잘못 세팅되었습니다. junseok-dataset에서 데이터셋을 로딩하는 부분을 다시 확인해주세요!")
        
        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN, 
                # These kwargs will be passed to _generate_examples
                gen_kwargs={
                    "filepaths": train_dataset,
                    "split": "train"
                }
            ),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION,
                # These kwargs will be passed to _generate_examples
                gen_kwargs={
                    "filepaths": val_dataset,
                    "split": "val"
                }
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                # These kwargs will be passed to _generate_examples
                gen_kwargs={
                    "filepaths": test_dataset,
                    "split": "test"
                }
            )
        ]


    # method parameters are unpacked from `gen_kwargs` as given in `_split_generators`
    def _generate_examples(self, filepaths: list[str], split: str):

        print(f'config name = {self.config.name}')
        
        key = -1
        for filepath in filepaths:
            with open(filepath, "r", encoding="latin-1") as f:
                key += 1
                codes = "".join(f.read().splitlines(keepends=True))
                yield key, {"text": codes}
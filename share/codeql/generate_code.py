import subprocess
from pprint import pprint
import linecache
import re
import os
from uuid import uuid4
from transformers import pipeline
from itertools import repeat
from transformers import AutoTokenizer, AutoModelForCausalLM
import sys
from tqdm import tqdm
import argparse



insecure_path = "/home/junseok/workdir/transformers/examples/pytorch/language-modeling/junseok-dataset/all-dataset/test.txt"
secure_path = "/home/junseok/workdir/transformers/examples/pytorch/language-modeling/junseok-dataset/secure-dataset/test.txt"

insecure_only_path = "/home/junseok/workdir/transformers/examples/pytorch/language-modeling/insecure_file_abs_paths.txt"

class FunctionInfo():
    
    def __init__(
        self, 
        function_name: str, 
        function_start_line_no: int, 
        function_end_line_no: int, 
        function_prototype: str,
        include_list = list[str]
    ) -> None:
        self.name = function_name
        self.start = function_start_line_no
        self.end = function_end_line_no
        self.prototype = function_prototype
        self.include_list = include_list
        
    def to_string(self) -> str:
        joined_include_list = "".join(self.include_list)
        
        return f"name({self.name}) ," + \
                f"start({self.start}) ," + \
                f"end({self.end}) ," + \
                f"prototype({self.prototype}) ," + \
                f"joined include_list({joined_include_list}) "


def extract_includes(sourcepath):
    include_list = []
    if os.path.exists(sourcepath):
        with open(sourcepath, 'r', encoding='latin-1') as sf:
            for line in sf:
                sanitize = ''.join(line.split())
                if sanitize.startswith('#include'):
                    include_list.append(line)
    return include_list


def subprocess_out_to_string(subprocess_out):
    return subprocess_out.decode('utf-8')


def get_function_info_list(c_file_name, wanted_function_name = None) -> list[FunctionInfo]:
    """
        `wanted_function_name`: 여러 개의 함수 이름과 라인 넘버 중에서 이 이름을 포함하는 함수에 대한 정보를 획득할 것이다.
    
        key: function name
        value: the start line number of the function name
    """
    ret = list()
    
    # other options
    # option1: f'ctags -x --c-kinds=pf --_xformat="%-16n %4n %-16f %C %s" {c_file_name}'
    # option2: f"ctags -x --c-kinds=f {c_file_name}"
    # option3: f"ctags --c-kinds=pf --fields=+neS -o - {c_file_name}"
    
    ctags_command = "ctags --c-kinds=f --fields=+Sne" + " -o - " + c_file_name
    # ctags --c-kinds=pf --fields=+ne -o - --_xformat="1111111111%N:%{typeref}:%{signature}" test.c
    # subprocess를 이용하여 ctags 명령어 실행
    subprocess_output = subprocess_out_to_string( subprocess.check_output(ctags_command, shell=True, timeout=10) )
    
    # print(f"subprocess_output: ({subprocess_output})")
    
    subprocess_output_lines = list(filter(lambda x: len(x) != 0, subprocess_output.split('\n')))
    
    
    for line in subprocess_output_lines:
        # ctags 명령어 실행결과물을 1줄씩 처리
        ctags_outputs = list(filter(lambda x: x != '', line.split('\t')))
        
        function_type = function_sig = ""
        function_start_no = function_end_no = -1
        function_name = ctags_outputs[0]
        for ctags_output in ctags_outputs:
            if "line:" in ctags_output:
                function_start_no = int(re.findall(r'\d+', ctags_output)[0])
            if "end:" in ctags_output:
                function_end_no = int(re.findall(r'\d+', ctags_output)[0])
            if "typeref:typename:" in ctags_output:
                function_type = ctags_output.replace("typeref:typename:", "")
            if "signature:" in ctags_output:
                function_sig = ctags_output.replace("signature:", "")

        if function_type == "" or function_sig == "" or function_start_no == -1 or function_end_no == -1:
            continue
        
        function_prototype = f"{function_type} {function_name}{function_sig}"
        include_list = extract_includes(c_file_name)

        function_info = FunctionInfo(function_name, function_start_no, function_end_no, function_prototype, include_list)
        
        
        ret.append(function_info)
        
        
        # print(function_name)
        # print(function_line_number)
        # if (wanted_function_name is not None) and (wanted_function_name in function_name):
        #     print(f"wanted_function_name: ({wanted_function_name})")
        #     print(f"function_name: ({function_name})")
        #     ret[function_name] = int(function_line_number)
    
    # pprint(ret)
    return ret


def open_and_collect_prototypes() -> list[FunctionInfo]:
    
    # secure한 모델도 모든 데이터셋에 대한 프로토타입을 가져다가 code-generation을 해야 한다.
    path = insecure_only_path
    
    function_info_list = list()
    
    
    with open(path, "r") as filelist:
        cfilepaths = filelist.read().splitlines()
        for cfilepath in cfilepaths:
            function_info_list.extend(get_function_info_list(cfilepath.replace('.txt', '.c')))
            
    return function_info_list


def make_prompts(function_info_list: list[FunctionInfo]):
    # 동일한 내용을 가진 `N`개의 프롬프트를 생성할 것이다. 똑같은 함수 프로토타입에 대해 `N`개의 코드를 생성해야하기 때문이다.
    N = 10
    
    prompts = list()
    for function_info in function_info_list:
        prompts.extend(list(repeat(function_info.prototype, N)))
    
    return prompts


def main(is_secure: bool, out_dir: str, model_path: str):
    
    ### 모델 옵션 ###
    print("[init_model] model initialization starts!")
    
    # model_path = "Salesforce/codegen-350M-multi"
    device_number = 1 if is_secure else 0    
    
    pipe = pipeline("text-generation", model=model_path, device=device_number, batch_size=80)
    
    model = AutoModelForCausalLM.from_pretrained(model_path)
    pipe.tokenizer.pad_token_id = model.config.eos_token_id
    
    print("Salesforce/codegen-350M-multi 모델 로딩 완료!")
    
    #print(f"[init_model] model_path: {}")
    print(f"[init_model] device_number: {device_number}")
    
    print("[init_model] model initialization is done!")
    
    if pipe is None:
        raise Exception("pipeline is not initialized yet.")
    
    os.makedirs(out_dir, exist_ok=True)
    
    print("[main] collecting function info starts!")
    function_info_list = open_and_collect_prototypes()
    
    ### prototype에 대해 distinct한 것들만 따로 모은다.
    function_info_list = list({function_info.prototype: function_info for function_info in function_info_list}.values())
    print("[main] collecting function info is done!")

    
    ### 같은 프로토타입에 대해 총 `N`번 코드를 생성할 것이다.
    count = 0
    
    prototype_dir = ""
    prototype_dir_count = 0
    
    N = 10
    
    chunk_size = 8
    chunks = [function_info_list[i:i+chunk_size] for i in range(0, len(function_info_list), chunk_size)]
    chunk_count = 0
    
    for chunk in tqdm(chunks):
        print(f"[{chunk_count}] 청크 하나 시작합니다.")
        print(f"len(chunk): {len(chunk)}")
        
        prototypes = list()
        joined_includes = list()
        for function_info in chunk:
            prototypes.extend(list(repeat(function_info.prototype, N)))
            joined_includes.extend(list(repeat("".join(function_info.include_list), N)))
    
        print(f"len(prototypes): {len(prototypes)}")

        for prototype, joined_include, output in zip(prototypes, joined_includes, pipe(prototypes, do_sample=True, max_new_tokens=200, temperature=1)):
            
                if count % N == 0:
                    os.chdir(out_dir)
                    prototype_dir = f"[[{prototype_dir_count}]]@{prototype.replace(' ', '_')[:15]}"
                    os.mkdir(prototype_dir)
                    prototype_dir_count += 1
                
                output_file = os.path.join(os.path.join(out_dir, prototype_dir), f"[{count}].c")
                with open(output_file, "w") as f:
                    f.write(joined_include)
                    f.write("\n")
                    f.write(output[0]["generated_text"])
                    f.write("\n")
                
                print(output[0]["generated_text"])
                print("==================================")
                
                count += 1
                
        chunk_count += 1
              
                # function_info_list = get_function_info_list(filename)    
                # function_info = min(function_info_list, key=lambda x: x.start)
                # print(function_info.to_string())
                # test_result.extend(get_function_info_list(filename))
            
            
if __name__ == "__main__":
    # e.g.) exec command: python3.10 generate_code.py --type=secure --out_dir=/home/junseok/workdir/share/data/output/code-generation/v4-test
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type", 
        type=str,
        choices=['secure', 'insecure'] ,
        help="What model-type will you use when generating code? "
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        help="The generated code will be stored in 'out_dir' directory. "
    )
    parser.add_argument(
        "--model_path",
        type=str,
        help="The trained custom model path. e.g.) '/tmp/cuda-junseok-clm-secure' "
    )
    args = parser.parse_args()
    
    
    is_secure = True if args.type == "secure" else False
    
    main(is_secure, args.out_dir, args.model_path)
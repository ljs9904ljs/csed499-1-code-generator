import argparse
import subprocess
import os
import re
import uuid
from pathlib import Path
import textwrap
import inspect



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
    
    def get_mockmain_call_string(self) -> str:
        """
        e.g.) 
        if a function prototype is... ==>>  int encode_audio(StreamingContext * decoder,StreamingContext * encoder,AVFrame * input_frame)
        then return value is... ==>>  encode_audio(argv[1], argv[2], argv[3]);
        
        """
        args_count = self.prototype.count(",")
        return f'{self.name}({", ".join(["argv" + "[" + str(i) + "]" for i in range(1, args_count + 2)])});'
        


def extract_includes(sourcepath) -> list[str]:
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


def get_function_info_list(c_file_abs_path: str) -> list[FunctionInfo]:
    """
        `c_file_abs_path`: absolute path of a c_file
    """
    
    ret = list()
    
    # other options ( If you want to these commands below, you must install and use 'universal ctags' ('exuberant ctags' doesn't work. ))
    # option1: f'ctags -x --c-kinds=pf --_xformat="%-16n %4n %-16f %C %s" "{c_file_name}"'
    # option2: f'ctags -x --c-kinds=f "{c_file_name}"'
    # option3: f'ctags --c-kinds=pf --fields=+neS -o - "{c_file_name}"'
    
    ctags_command = f'ctags --c-kinds=f --fields=+Sne -o - "{c_file_abs_path}"'
    
    # print(ctags_command)
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
        include_list = extract_includes(c_file_abs_path)

        function_info = FunctionInfo(function_name, function_start_no, function_end_no, function_prototype, include_list)
        
        
        ret.append(function_info)
        
    ret = list(sorted(ret, key=lambda x: x.start))
    return ret


def generate_mockmain_files(src_c_file: str, function_info_list: list[FunctionInfo], out_dir: str, is_header_included: bool) -> None:
    
    mockmain_filename_prefix = "mockmain"
    
    with open(src_c_file, "r", encoding="latin-1") as original_c_file:
        original_content_lines = original_c_file.read().splitlines(keepends=True)
        
        if not is_header_included:
            original_content_lines = filter(lambda line: "#include" not in line, original_content_lines)
        
        original_content = "".join(original_content_lines)
        
        for function_info in function_info_list:
            src_c_filename, ext = os.path.splitext(os.path.basename(src_c_file))
            new_filename = mockmain_filename_prefix + "_" + src_c_filename + "_" + str(uuid.uuid4()) + ext
            
            with open(Path(out_dir) / Path(new_filename), "w", encoding="latin-1") as new_c_file:
                new_c_file.write(
                    """
                    %s


                    int main(int argc, char** argv) {
                        %s
                    }
                                        
                    """ % (original_content, function_info.get_mockmain_call_string())
                )
                
        


def main(src_c_file: str, out_dir: str, header: int) -> None:
    is_header_included = True if header == 1 else False
    
    function_info_list = get_function_info_list(os.path.abspath(src_c_file))
    
    generate_mockmain_files(
        src_c_file,
        function_info_list,
        out_dir,
        is_header_included
    )
    


if __name__ == '__main__':
    
    ### To run this 'mockmain_v2.py', you must install 'universal ctags'. ('exuberant ctags' doesn't work. )
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--src_c_file", 
        type=str, 
        help="This 'src_c_file' will be converted into several mockmain c files. "
    )
    parser.add_argument(
        "--out_dir", 
        type=str, 
        help="The generated mockmain c files will be stored in this 'out_dir'. If the 'out_dir' doesn't exist, create every directory that is contained in the path."
    )
    parser.add_argument(
        "--header", 
        type=int, 
        choices=[1, 0], 
        default=1, 
        help="[default: 1] 1 if you want to add the 'include<header file> lines' of the original 'src_c_file' to the mockmain c files, 0 otherwise. "
    )

    args = parser.parse_args()
    
    # e.g.) exec command: python3.10 mockmain_v2.py --src_c_file=/home/junseok/workdir/hf-dataset/all-c-files-master-main/3_transcoding.c --out_dir=/home/junseok/workdir/tmp --header=0
    # e.g.) src_c_file: /home/junseok/workdir/hf-dataset/all-c-files-master-main/3_transcoding.c
    
    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)
    
    main(args.src_c_file, args.out_dir, args.header)
    
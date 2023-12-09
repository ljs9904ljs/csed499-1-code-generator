import subprocess
import sys
from pprint import pprint

def subprocess_out_to_string(subprocess_out):
    return subprocess_out.decode('utf-8')


def get_function_name_and_start_line_number(c_file_name) -> dict:
    """
        key: function name
        value: the start line number of the function name
    """
    ret = dict()
    
    ctags_command = f"ctags -x --c-kinds=f {c_file_name}"
    
    # subprocess를 이용하여 ctags 명령어 실행
    subprocess_output = subprocess_out_to_string( subprocess.check_output(ctags_command, shell=True) )
    subprocess_output_lines = list(filter(lambda x: len(x) != 0, subprocess_output.split('\n')))
    for line in subprocess_output_lines:
        # ctags 명령어 실행결과물을 1줄씩 처리
        ctags_outputs = list(filter(lambda x: x != '', line.split(' ')))
        
        function_name = ctags_outputs[0]
        function_line_number = ctags_outputs[2]
        
        print(function_name)
        print(function_line_number)
        
        ret[function_name] = int(function_line_number)
    
    pprint(ret)
    return ret


def get_function_end_line_number(c_file_name: str, function_start_line_number: int) -> int:
    awk_command = "awk 'NR > " + str(function_start_line_number) + " && /^}$/ { print NR; exit }' first=$FIRST_LINE " + c_file_name
    
    ret = int(subprocess_out_to_string( subprocess.check_output(awk_command, shell=True) ))
    
    print("function end line number: ", ret)
    return ret


def get_function_info_dict(c_file_name: str) -> dict:
    # key: function_name
    # value: tuple of (start_line_number, end_line_number)
    function_info_dict = dict()
    
    function_name_and_start_line_number_dict = get_function_name_and_start_line_number(c_file_name)
    for function_name, start_line_number in function_name_and_start_line_number_dict.items():
        end_line_number = get_function_end_line_number(
            c_file_name,
            start_line_number
        )
        function_info_dict[function_name] = (start_line_number, end_line_number)
    
    print("\n\n\n\n\n")
    pprint(function_info_dict)
    
    return function_info_dict


def main(c_file_name: str):
    get_function_info_dict(c_file_name)



if __name__ == "__main__":
    c_file_name = sys.argv[1]
    
    main(c_file_name)
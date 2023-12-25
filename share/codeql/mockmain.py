import sys
import os
from pathlib import Path
import uuid

def extract_includes(sourcepath):
    include_list = []
    if os.path.exists(sourcepath):
        with open(sourcepath, 'r', encoding='latin-1') as sf:
            for line in sf:
                sanitize = ''.join(line.split())
                if sanitize.startswith('#include'):
                    include_list.append(line)
    return include_list

def extract_name(function_def):
    function_def = function_def.strip()
    if function_def.count('{') > 0:
        pos = function_def.find('{')
        function_def = function_def[:pos].strip()
    # print(function_def)
    parcnt = 0
    pos = 0
    for i, c in enumerate(reversed(function_def)):
        if c == ')':
            parcnt += 1
        elif c == '(':
            parcnt -= 1
        if parcnt == 0:
            pos = len(function_def) - i -1
            break
    # print(function_def[:pos])
    splitdef = function_def[:pos].split()
    for token in reversed(splitdef):
        if token == ')':
            continue
        while token.startswith('*'):
            token = token.strip('*')
        while token.endswith(')') or token.startswith('('):
            token = token.strip('(')
            token = token.strip(')')
        return token

if __name__ == '__main__':

    argv = sys.argv

    sourcepath = argv[1]
    _functiondir = argv[2]
    functiondir = os.path.abspath(_functiondir)
    outpath = argv[3]
    is_header_included = True if argv[4] == '1' else False # 1 or 0
    
    
    if argv[4] != '1' and argv[4] != '0':
        raise Exception("argv[4] must be '1' or '0'. ")
    
    #print(functiondir)
    #print(os.path.abspath(functiondir))
    
    include_list = extract_includes(sourcepath)
    # print(include_list)
    if os.path.exists(functiondir):
        for functionfile in os.listdir(functiondir):
            # print(f"function file : ({functionfile})")
            with open(functiondir / Path(functionfile), 'r', encoding='latin-1') as ff:
                funcdef = ff.readline()
                comma_cnt = funcdef.count(',')
                notclosed_cnt = funcdef.count('(') - funcdef.count(')')
                notopened = True
                if funcdef.count('(') > 0:
                    notopened = False
                while notclosed_cnt != 0 or notopened:
                    nextline = ff.readline()
                    if nextline.count('(') > 0:
                        notopened = False
                    comma_cnt += nextline.count(',')
                    parenthesis = nextline.count('(') - nextline.count(')')
                    notclosed_cnt += parenthesis
                    funcdef += nextline
                funcdef = ' '.join(funcdef.split())
                no_arg_cnt = ''.join(funcdef.split()).count('()')
                if no_arg_cnt > 0 and comma_cnt == 0:
                    comma_cnt = -1
                function_name = extract_name(funcdef)
                Path(outpath).mkdir(parents=True, exist_ok=True)
                
                with open(outpath / Path(f"{uuid.uuid1()}@{functionfile}"), 'w', encoding='latin-1') as of:
                    
                    if is_header_included:
                        for includeline in include_list:
                            of.write(includeline)
                        
                    of.write("\n")
                    ff.seek(0)
                    for line in ff:
                        of.write(line)
                    of.write("\n")
                    of.write("int main (int argc, char** argv) {\n\n")
                    call_argument = '()'
                    if comma_cnt >= 0:
                        call_argument = '(argv[1]'
                        for comma in range(comma_cnt):
                            call_argument += f", argv[{comma+2}]"
                        call_argument += ')'
                    else:
                        call_argument = '()'
                    of.write(f"    {function_name}{call_argument};\n\n")
                    of.write("    return 0;\n")
                    of.write("}\n")
    else:
        print(f"({functiondir}) NOT EXIST.")
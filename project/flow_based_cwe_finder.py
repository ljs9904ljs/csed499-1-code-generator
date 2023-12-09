import os
import glob


PROJECT_ROOT_DIR_PATH = '/home/wsl-junseok/workdir/codeql/cpp/ql/src/Security/CWE'


def find_all_ql_file_abs_paths_in_dir(dir_name: str) -> list[str]:
    # Specify the directory path and the file extension you want to search for
    dir_path = PROJECT_ROOT_DIR_PATH + "/" + dir_name
    file_ext = '*.ql' 

    # Create a list of file paths that match the given extension
    matching_abs_paths = glob.glob(os.path.join(dir_path, file_ext))
    
    return matching_abs_paths


def is_path_problem(file_abs_path: str) -> bool:
    with open(file_abs_path) as f:
        for line in f:
            if "@kind" in line and "path-problem" in line:
                return True
        return False


def get_all_cwe_dir_names() -> list[str]:
    return os.listdir(PROJECT_ROOT_DIR_PATH)


# CWE-20, 119, 120, 190
def get_all_flow_based_cwes() -> list[str]:
    flow_based_cwe_paths = list()
    
    for cwe_dir_name in get_all_cwe_dir_names():
        ql_file_abs_paths = find_all_ql_file_abs_paths_in_dir(cwe_dir_name)
        count = 0
        not_count = 0
        for path in ql_file_abs_paths:
            if is_path_problem(path):
                count += 1
                flow_based_cwe_paths.append(path)
            else:
                not_count += 1
                
        # logging
        log = f"CWE name ({cwe_dir_name}) , ql files count ({len(ql_file_abs_paths)}) , path_problem count ({count}) , other problems count ({not_count})"
        if count != 0 and not_count != 0:
            log += "  **********"
        print(log)
        
    return flow_based_cwe_paths



cwe_numbers = set()
for cwe in sorted(get_all_flow_based_cwes(), key=lambda x: x.split("/")[-2]):
    chunks = cwe.split("/")
    print(chunks[-2] + " === " + chunks[-1])
    cwe_numbers.add(chunks[-2])

for n in sorted(cwe_numbers):
    print(n)


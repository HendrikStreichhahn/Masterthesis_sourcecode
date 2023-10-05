import os

UNDEFINED_STRING= "undefined"

def char_n_times(n: int, char: str):
    res = ""
    for _ in range(0, n):
        res += char
    return res

def addLine(startStr: str, newLine: str):
    return startStr + "\n" + newLine

def cleanify_string(val: str):
    invalidChars= [":", "."]
    res = val
    for char in invalidChars:
        res= res.replace(char, "_")
    return res

# returns path_b relative to path_a
def make_relative_path(path_a, path_b):
    try:
        absolute_path_a = os.path.abspath(path_a)
        if os.path.isdir(path_a):
            folder_a, file_a = path_a, ""
        else:
            folder_a, file_a = os.path.split(absolute_path_a)
        absolute_path_b = os.path.abspath(path_b)
        if os.path.isdir(path_b):
            folder_b, file_b = path_b, ""
        else:
            folder_b, file_b = os.path.split(absolute_path_b)
        relative_path = os.path.relpath(folder_b, folder_a) + "/" + file_b
        return relative_path
    except ValueError as e:
        return str(e)

def path_remove_front(path):
    if path.startswith("../"):
        return path[3:]
    else:
        return path

def get_folder(path: str):
    if os.path.isdir(path):
        return path
    else:
        path,_ = os.path.split(path)
        return path

# returns the absolute path to a path, that is relative to the execution path
def get_abs_path(path, rel_base = os.getcwd()):
    rel_base = get_folder(rel_base)
    blupp = os.path.join(rel_base, path)
    norm_path = os.path.normpath(blupp)
    return os.path.abspath(norm_path)

def get_bool_string(val):
    if val:
        return "true"
    else:
        return "false"

def get_string_array(array: list([str])):
    res = "["
    for itm in array:
        res += f"\"{itm}\" "
    res = res.rstrip(', ') + "]"

def get_tag_pass_string(
        array: list([str]),
        tag_prefix: str = "",
        delim: str = "\""):
    if len(array) == 0:
        return "[]"
    res: str = "["
    for tag in array:
        res += f"{delim}{tag_prefix}{tag}{delim},"
    res = res[:-1] + "]"
    return res

def get_service_file_name_no_ending(instance_id: str,
                          command_no: str):
    return cleanify_string(f"{instance_id}_command_service_{command_no}") 

def get_service_file_name(instance_id: str,
                          command_no: str):
    return get_service_file_name_no_ending(instance_id, command_no)+ ".service"
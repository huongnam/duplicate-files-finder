import argparse
import os
import hashlib
import json


def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=str, help='the root directory to start scanning for duplicate files')
    args = parser.parse_args()
    path = args.path
    return path


def scan_files(path):
    '''
    return a flat list of files scanned recursively from this specified path
    '''
    files = []
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            files.append(os.path.abspath((os.path.join(root, filename))))
    # print(files)
    return files


# def remove_empty_files(files):
#     """
#     return a list of non-empty files
#     """
#     temp = [_file for _file in files if os.path.getsize(_file) == 0]
#     for file in temp:
#         files.remove(file)
#     return files
def group_files_by_key(file_path_names, find_key):
    groups = {}
    for file in file_path_names:
        size = os.path.getsize(file)
        if size == 0:
            continue
        key = find_key(file)
        groups.setdefault(key, []).append(file)
    return [group for group in groups.values() if len(group) > 1]


def group_files_by_size(file_path_names):
    """ returns a list of groups of at least two
        files that have the same size """
    return group_files_by_key(file_path_names, os.path.getsize)

    # # files = remove_empty_files(file_path_names)
    # # print(files)
    # groups = {}
    # for file in file_path_names:
    #     _size = os.path.getsize(file)
    #     if _size == 0:
    #         continue
    #     groups.setdefault(_size, []).append(file)
    # # print(groups)
    # # list_of_groups = [group for group in groups.values() if len(group) > 1]
    # # print(list_of_groups)
    # return [group for group in groups.values() if len(group) > 1]


def get_file_checksum(file):
    with open(file, "r") as f:
        content = f.read()
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def group_files_by_checksum(file_path_names):
    groups = {}
    for file in file_path_names:
        checksum = get_file_checksum(file)
        groups.setdefault(checksum, []).append(file)
    return [group for group in groups.values() if len(group) > 1]


def find_duplicate_files(file_path_names):
    result = []
    groups = group_files_by_size(file_path_names)
    for group in groups:
        duplicated_files = group_files_by_checksum(group)
        for duplicated_file in duplicated_files:
            result.append(duplicated_file)
        # result.append(duplicated_file for duplicated_file in duplicated_files)
    print(result)
    return result

def convert_to_json(content):
    return json.dumps(content)

def main():
    path = parse_command_line()
    file_path_names = scan_files(path)
    # group_files_by_size(file_path_names)
    # group_files_by_checksum(file_path_names)
    return convert_to_json(find_duplicate_files(file_path_names))


if __name__ == '__main__':
    main()

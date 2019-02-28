#!/usr/bin/env python
import argparse
import os
from hashlib import md5
import json
from sys import stderr


def parse_command_line():
    '''
    Read command line to get arguments
    '''
    parser = argparse.ArgumentParser(description='Duplicate files finder')
    parser.add_argument('-p', '--path', required=True, type=str,
                        help='the root directory to start scanning\
                        for duplicate files')
    parser.add_argument('-a', action="store_true",
                        help='show hidden files')
    parser.add_argument('-c', action="store_true",
                        help='group by first chunks before\
                        grouping by checksum')
    args = parser.parse_args()
    return args


def is_valid_path(path):
    '''
    Check if path is a directory and we have access to it; else show the error
    then exit the program
    '''
    if os.path.isdir(path) and os.access(path, os.R_OK):
        return True
    else:
        stderr.write("{}: Invalid path.\n".format(path))
        exit()


def scan_files(path, hidden=False):
    '''
    Return a flat list of files scanned recursively from this specified path
    @param hidden: Whether or not the hidden files are shown
    '''
    # print("heheheh")
    if is_valid_path(path):
        # print("haha")
        files = []
        for root, dirnames, filenames in os.walk(path):
            if hidden is False:
                # ignore hidden files
                dirnames = [dirname for dirname in dirnames
                            if dirname[0] != "."]
                filenames = [filename for filename in filenames
                             if filename[0] != "."]
            for filename in filenames:
                # ignore symlink and inaccessible files
                if os.path.islink(os.path.join(root, filename)) or \
                        not os.access(os.path.join(root, filename), os.R_OK):
                    continue
                files.append(os.path.abspath((os.path.join(root, filename))))
    return files


def group_files_by_key(file_path_names, option):
    ''' Group files by key, which can be:
    - size
    - checksum
    - content: the first 8 bytes of file
    Group = {"keyA": [file1, file2]
             "keyB": [file3, file4]}
    For each file in file_path_names, find the key according to options.
    The files that have the same key will be added into its value.
    Return a list of group's values when there are more than one file that
    have the same key.
    '''
    groups = {}
    for file in file_path_names:
        if option == "size":
            size = os.path.getsize(file)
            # ignore empty files
            if size == 0:
                continue
            key = os.path.getsize(file)
        if option == "checksum":
            key = get_file_checksum(file)
        if option == "content":
            with open(file, "rb") as f:
                first_8_bytes = f.read(8)
            key = first_8_bytes
        groups.setdefault(key, []).append(file)
    return [group for group in groups.values() if len(group) > 1]


def group_files_by_size(file_path_names):
    """ Return a list of groups of at least two
    files that have the same size """
    return group_files_by_key(file_path_names, "size")


def group_files_by_content(file_path_names):
    """ Return a list of groups of at least two
    files that have the same first 8 bytes """
    return group_files_by_key(file_path_names, "content")


def chunk_file(file, chunk_size=1024):
    ''' Divide file into chunks '''
    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            return None
        yield chunk


def get_file_checksum(file):
    ''' Generate a hash value for a File '''
    hashobj = md5()
    with open(file, "rb") as f:
        for chunk in chunk_file(f):
            hashobj.update(chunk)
        return hashobj.hexdigest()


def group_files_by_checksum(file_path_names):
    """ Return a list of groups of at least two
    files that have the same hash value """
    return group_files_by_key(file_path_names, "checksum")


def find_dup_files_by_size_and_checksum(group_by_size, result):
    ''' Find duplicated files by grouping them in size, then generate
    a hash value for each file in group and group those that have the same
    hash value'''
    groups_by_checksum = group_files_by_checksum(group_by_size)
    for duplicated_file in groups_by_checksum:
        result.append(duplicated_file)
        return result


def find_dup_files_by_size_and_content_and_checksum(group_by_size, result):
    ''' Find duplicated files by grouping them in size, then group those that
    have the same first 8 bytes. After that do the function above.
    '''
    groups_by_content = group_files_by_content(group_by_size)
    for group_by_content in groups_by_content:
        result = find_dup_files_by_size_and_checksum(group_by_content, result)
    return result


def find_duplicate_files(file_path_names, chunks=True):
    ''' Return a list of groups of duplicate files '''
    result = []
    groups_by_size = group_files_by_size(file_path_names)

    for group_by_size in groups_by_size:
        if chunks is True:
            result = find_dup_files_by_size_and_content_and_checksum(
                        group_by_size, result)
        else:
            result = find_dup_files_by_size_and_checksum(group_by_size, result)
    return result


def convert_to_json(content):
    ''' Convert to json format '''
    return json.dumps(content, indent=4)


def main():
    args = parse_command_line()
    path = args.path
    if args.a:
        file_path_names = scan_files(path, hidden=True)
    else:
        file_path_names = scan_files(path)
    if args.c:
        result = find_duplicate_files(file_path_names, "chunk")
    else:
        result = find_duplicate_files(file_path_names)
    print(convert_to_json(result))


if __name__ == '__main__':
    main()

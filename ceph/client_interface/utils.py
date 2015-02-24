from os import listdir, walk
from os.path import isfile, isdir, join
from pprint import pprint

def list_all_files_in_subdirs(root_dir):
    file_list = []
    for path, subdirs, files in walk(files_source_dir):
        for name in files:
            file_list.append(join(path, name))

def get_gridref_from_fpath(fpath):
    


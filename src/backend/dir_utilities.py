import os
import sys
import pandas as pd

rootDir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


def clear_directory(path = f"{rootDir}/data/uploads/"):
    '''
    FUNCTION to clear the uploads folder.
    '''
    try:
        os.chdir(path)
        path = os.getcwd()
        
        filelist = []
        for root, dirs, files in os.walk(path):
            for ff in files:
                os.remove(os.path.join(root,ff))
    except Exception as e:
        print(e)



def list_files(directory = f"{rootDir}/data/", ignore = ['.DS_Store']):
    '''
    FUNCTION to list all the files in a directory.
    input: directory, root as a string
    output: list of files
    '''
    try:
        os.chdir(directory)
        path = os.getcwd()
        filelist = []
        for root, dirs, files in os.walk(path):
            for ff in files:
                filelist.append(os.path.join(root,ff))
        filelist = [file for file in filelist if not any(skip in file for skip in ignore)]
        return filelist
    except Exception as e:
        print(e)



def search_data(filename):
    '''
    FUNCTION to search if a file is already in database and
    if a pre-processed version can be used.
    input: filename, name of file to be searched
    output:
    - bool, True if found, False if not found
    - df, dataframe of pre-processed data if found,
    empty dataframe if not found
    '''
    try:
        # search for filename with .csv extension
        if "." in filename:
            file = filename[:filename.rfind(".")] + '.csv'
        else:
            file = filename + '.csv'
        
        filelist = list_files(f"{rootDir}/data/")
        idx = [ff for ff in filelist if file in ff]
        
        # if a single file found, return True and dataframe
        if idx and len(idx) == 1:
            df = pd.read_csv(idx[0])
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            return True, df
        
        # otherwise, return False and empty dataframe
        else:
            return False, pd.DataFrame()
        
    except Exception as e:
        print(e)


        
def find_text_markers(text, match_strings):
    return all([text.find(str) >= 0 for str in match_strings])



def get_tree_structure(path = f"{rootDir}/data"):
    def get_subdirectory_structure(subpath):
        subdirs = [d for d in os.listdir(subpath) if os.path.isdir(os.path.join(subpath, d))]
        nodes = []
        for subdir in subdirs:
            subdir_path = os.path.join(subpath, subdir)
            node = {
                'value': subdir_path,
                'label': subdir,
                'children': get_subdirectory_structure(subdir_path)
            }
            nodes.append(node)
        return nodes

    if not os.path.exists(path):
        raise FileNotFoundError(f"The path {path} does not exist.")

    return get_subdirectory_structure(path)



def create_nested_file(dir_string, root_directory = f"{rootDir}/data"):
    def parse_directory_structure(dir_string):
        return dir_string.split('/')

    def create_filepath(root, dir_parts):
        current_path = os.path.abspath(root)
        for part in dir_parts[:-1]:
            # Exclude the last part, which is the filename
            current_path = os.path.join(current_path, part)
            if not os.path.exists(current_path):
                os.makedirs(current_path)
        filepath = os.path.join(current_path, dir_parts[-1])
        return filepath

    parts = parse_directory_structure(dir_string)
    filepath = create_filepath(root_directory, parts)
    return filepath

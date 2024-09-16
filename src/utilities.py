import os
import pandas as pd


def get_absolute_path(*relative_paths):
    """Utility function to construct absolute paths from relative paths."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *relative_paths))


class DataManager:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.tree_structure = self.get_tree_structure()
        self.file_list = self.list_files()
        self.duplicate_files = len(set(self.file_list)) < len(self.file_list)

    def get_tree_structure(self):
        path = self.data_dir
        
        def get_subdirectory_structure(subpath):
            subdirs = [d for d in os.listdir(subpath) if os.path.isdir(os.path.join(subpath, d))]
            return [
                {
                    'value': os.path.join(subpath, subdir),
                    'label': subdir,
                    'children': get_subdirectory_structure(os.path.join(subpath, subdir))
                }
                for subdir in subdirs
            ]
        if not os.path.exists(path):
            raise FileNotFoundError(f"The path {path} does not exist.")

        return get_subdirectory_structure(path)

    def create_nested_directory(self, dir_string):
        parts = dir_string.split('/')
        current_path = self.data_dir
        if len(parts) == 1:
            return current_path
        else:
            for part in parts[:-1]:
                current_path = os.path.join(current_path, part)
                os.makedirs(current_path, exist_ok=True)
            return os.path.join(current_path, parts[-1])

    def clear_directory(self, path):
        for root, _, files in os.walk(path):
            for file in files:
                os.remove(os.path.join(root, file))

    def list_files(self, ignore=None):
        directory = self.data_dir
        if ignore is None:
            ignore = ['.DS_Store','__pycache__','.git','env']
        
        file_list = []
        for root, _, files in os.walk(directory):
            for file in files:
                if not any(skip in file for skip in ignore):
                    file_list.append(os.path.join(root, file))
        return file_list

    def search_directory(self, filename):
        matching_files = [f for f in self.file_list if filename in f]
        if len(matching_files) < 1:
            return False
        return True

    def insert_file(self, content, destination):
        with open(destination, "wb") as f:
            f.write(content)
        return destination

    def retrieve_file(self, filename):
        if not filename.endswith('.csv'):
            raise TypeError("Only .csv files are retriveable.")
        filepath = get_full_path(filename)
        df = pd.read_csv(filename)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        return df

    def print_tree_structure(self, path=None, level=0, ignore=None):
        if path is None:
            path = self.data_dir
        
        if ignore is None:
            ignore = []
        
        indent = '|── ' * level  # each level of indentation
        folders = []
        
        try:
            for entry in os.listdir(path):
                full_entry_path = os.path.join(path, entry)
                if os.path.isdir(full_entry_path):
                    if entry not in ignore:
                        folders.append(f'{indent}{entry}')
                        sub_folders = self.print_tree_structure(full_entry_path, level + 1, ignore)
                        folders.extend(sub_folders)
        except PermissionError:
            print(f'Permission denied: {path}')  # Handle permission issues
        except FileNotFoundError:
            print(f'Directory not found: {path}')  # Handle invalid paths
        return folders

    def get_full_path(self, partial_path):
        clean_path = partial_path.lstrip('|── ').rstrip('/')
        
        for root, dirs, files in os.walk(self.data_dir):
            # get full path of file
            if "." in clean_path and clean_path in files:
                return root+"/"+clean_path
            
            # get full path of folder
            elif clean_path in dirs:
                return root+"/"+clean_path
        
        return None


DataDirectory = DataManager(get_absolute_path('../data'))

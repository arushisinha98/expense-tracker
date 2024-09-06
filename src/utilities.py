import os
import sys
import pandas as pd

rootDir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


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



def list_files(directory = f"{rootDir}/data/"):
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
            file = '/' + filename[:filename.rfind(".")] + '.csv'
        else:
            file = '/' + filename + '.csv'
        
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


        
def check_statement(text, match_strings):
    return all([text.find(str) >= 0 for str in match_strings])



def completed(df):
    '''
    FUNCTION to check if, minimally, all expenses have been classified. Note expenses are -ve amounts (i.e. outgoing); classification of incoming amounts (+ve) is optional.
    input: df, the dataframe
    output: bool
    '''
    try:
        if "Category" not in df.columns:
            return True
        else:
            idx1 = df[df["Category"].isin(expense_categories)].index
            idx2 = df[df["Amount"] < 0].index
            return set(idx1) >= set(idx2)
    except Exception as e:
        print(e)



def save_data(df, filename):
    '''
    FUNCTION to save processed data as .csv file in database.
    input:
    - df, the dataframe
    - filename, the name of the original file
    output: N/A
    '''
    try:
        clear_directory()
        # find filepath of original file and save csv
        filelist = list_files(rootDir)
        idx = [ff for ff in filelist if filename in ff]
        if idx:
            file = idx[0][:idx[0].rfind(".")] + '.csv'
            df.to_csv(file)
    except Exception as e:
        print(e)

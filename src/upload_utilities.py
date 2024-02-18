import os
import sys
import pandas as pd

from decouple import config
MASTER_DIRECTORY = config('MASTER_DIRECTORY')
MY_NAME = config('MY_NAME')
DBS, OCBC, IBKR, Endowus = config('DBS'), config('OCBC'), config('IBKR'), config('Endowus')
FD, SRS = config('FD'), config('SRS')
CPF, CDP = config('CPF'), config('CDP')

curr_dir = os.path.dirname(__file__)
sys.path.append(curr_dir)

from pdf_utilities import extract_text
from read_dbs import DBSStatement, SRSStatement, FDStatement
from read_ocbc import OCBCStatement
from read_ibkr import IBKRStatement
from read_endowus import EndowusStatement
from read_cpf import CPFStatement
from read_cdp import CDPStatement
from constants import expense_categories


def clear_directory(path = f"{MASTER_DIRECTORY}/data/uploads/"):
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


def list_files(directory = MASTER_DIRECTORY):
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
    FUNCTION to search if a file is already in database and if a pre-processed version can be used.
    input: filename, name of file to be searched
    output:
    - bool, True if found, False if not found
    - df, dataframe of pre-processed data if found, empty dataframe if not found
    '''
    try:
        # search for filename with .csv extension
        if "." in filename:
            file = '/' + filename[:filename.rfind(".")] + '.csv'
        else:
            file = '/' + filename + '.csv'
            
        filelist = list_files(f"{MASTER_DIRECTORY}/data/")
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
    

def process_upload(filename, bytes_data):
    '''
    FUNCTION to read uploaded document and assign location to save data.
    input: filename, name of file that was uploaded by user on frontend
    output: statement, class object created from file if successfully read
    '''
    try:
        # read file from uploads directory
        os.chdir(MASTER_DIRECTORY)
        text = extract_text(f"{MASTER_DIRECTORY}/data/uploads/{filename}")
        
        # if DBS Statement, copy raw file to DBS folder and return statement object
        if filename.endswith(".pdf") and check_statement(text, ["DBS", MY_NAME, DBS]):
            filepath = f"{MASTER_DIRECTORY}/data/SG/DBS/{filename}"
            with open(filepath, 'wb') as f:
                f.write(bytes_data)
            statement = DBSStatement(filepath)
            return statement
        
        # if OCBC Statement, copy raw file to OCBC folder and return statement object
        elif filename.endswith(".pdf") and check_statement(text, ["OCBC 90.N CARD", MY_NAME, OCBC]):
            filepath = f"{MASTER_DIRECTORY}/data/SG/OCBC/{filename}"
            with open(filepath, 'wb') as f:
                f.write(bytes_data)
            statement = OCBCStatement(filepath)
            return statement
            
        # if IBKR Statement, save processed dataframe to IBKR folder and return statement object
        elif filename.startswith(IBKR) and filename.endswith(".csv"):
            filepath = f"{MASTER_DIRECTORY}/data/uploads/{filename}"
            statement = IBKRStatement(filepath)
            df = statement.get_transactions()
            df.to_csv(f"{MASTER_DIRECTORY}/data/SG/IBKR/{filename}")
            return statement
            
        # if DBS (FD / SRS) Statement, save processed dataframe to relevant folder and return statement object
        elif filename.endswith(".pdf") and (check_statement(text, ["Supplementary Retirement Scheme", MY_NAME, SRS]) or check_statement(text, ["Fixed Deposit", MY_NAME, FD])):
            
            filepath = f"{MASTER_DIRECTORY}/data/SG/FD or SRS/{filename}"
            with open(filepath, 'wb') as f:
                f.write(bytes_data)
            
            statement1 = SRSStatement(filepath)
            statement2 = FDStatement(filepath)
            if statement1:
                return statement1 # SRS detected only
            else:
                return statement2 # auto-appends SRS to FD if detected in statement
            
        # if Endowus Statement, save processed dataframe to Endowus folder and return statement object
        elif filename.startswith("Endowus") and filename.endswith(".pdf") and check_statement(text, ["Endowus", MY_NAME, Endowus]):
            filepath = f"{MASTER_DIRECTORY}/data/SG/Endowus/{filename}"
            with open(filepath, 'wb') as f:
                f.write(bytes_data)
            statement = EndowusStatement(filepath)
            return statement
            
        # if CPF Statement, save processed dataframe to CPF folder and return statement object
        elif ("Yearly Statement of Account" in filename) and filename.endswith(".pdf") and check_statement(text, ["CPF", MY_NAME, CPF]):
            filepath = f"{MASTER_DIRECTORY}/data/SG/CPF/{filename}"
            with open(filepath, 'wb') as f:
                f.write(bytes_data)
            statement = CPFStatement(filepath)
            return statement
            
        # if CDP Statement, save processed dataframe to CDP folder and return statement object
        elif filename.endswith(".pdf") and check_statement(text, ["CDP", MY_NAME, CDP[-4:]]):
            filepath = f"{MASTER_DIRECTORY}/data/SG/CDP/{filename}"
            with open(filepath, 'wb') as f:
                f.write(bytes_data)
            statement = CDPStatement(filepath)
            return statement
            
        else:
            return False
        
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
        filelist = list_files(MASTER_DIRECTORY)
        idx = [ff for ff in filelist if filename in ff]
        if idx:
            file = idx[0][:idx[0].rfind(".")] + '.csv'
            df.to_csv(file)
    except Exception as e:
        print(e)

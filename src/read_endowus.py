import os
import sys
from datetime import datetime
import pandas as pd

curr_dir = os.path.dirname(__file__)
sys.path.append(curr_dir)

from dtype_conversions import str_to_float
from pdf_utilities import extract_text, select_text


class EndowusStatement:
    '''
    CLASS OBJECT for Endowus Investment Statement.
    input: filepath, to pdf file of bank statement
    '''
    def __init__(self, filepath):
        self.filepath = filepath
    
    
    def get_date(self):
        '''
        FUNCTION to read end-of-statement date
        output: datetime object
        '''
        try:
            text = extract_text(self.filepath)
            selected = select_text(text, "Investment Ending Balance", "Returns")
            selected = selected[selected.find(")")+1:].split("\n")
            return datetime.strptime(selected[1], '%d %b %Y')
        except Exception as e:
            print(e)
    
    
    def get_balance(self):
        '''
        FUNCTION to read end-of-statement balance (in SGD)
        output: balance, as a numerical value
        '''
        try:
            text = extract_text(self.filepath)
            selected = select_text(text, "Investment Ending Balance", "Returns")
            selected = selected[selected.find(")")+1:].split("\n")
            return str_to_float(selected[2])
        except Exception as e:
            print(e)
    
    
    def get_transactions(self):
        '''
        FUNCTION to read the total balance (in SGD)
        output: dataframe with columns: Date, Balance
        '''
        try:
            new_df = pd.DataFrame(columns = ["Date", "Balance"], data = [[self.get_date(), self.get_balance()]])
            return new_df
        except Exception as e:
            print(e)

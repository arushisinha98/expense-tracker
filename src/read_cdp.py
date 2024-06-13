import os
import sys
from datetime import datetime
import pandas as pd
import numpy as np

curr_dir = os.path.dirname(__file__)
sys.path.append(curr_dir)

from dtype_conversions import str_to_float
from pdf_utilities import extract_text, select_text


class CDPStatement:
    '''
    CLASS OBJECT for CDP Account Statement.
    download instructions: E-Statements >> CDP Securities Account Statements
    '''
    def __init__(self, filepath):
        self.filepath = filepath
        
    def get_date(self):
        filepath = self.filepath
        mmyyyy = filepath[-12:-4]
        return datetime.strptime(f" 1 {mmyyyy}", '%d %b %Y')
        
    def get_transactions(self):
        '''
        FUNCTION to read the total balance (in SGD)
        output: dataframe with columns: Date, Balance
        '''
        try:
            text = extract_text(self.filepath)
            
            data = select_text(text, "\nSGD\nSGD\n", "\nTOTAL: SGD")
            nrows = data.count("SB")
            transactions = np.array(data.split('\n')).reshape((nrows,6))
            
            balance = sum([str_to_float(val) for val in transactions[:,3]])
            
            new_df = pd.DataFrame(columns = ["Date", "Balance"], data = [[self.get_date(), balance]])
            
            return new_df
        except Exception as e:
            print(e)

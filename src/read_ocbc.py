import os
import sys
from datetime import datetime
import pandas as pd
import numpy as np
import sys

curr_dir = os.path.dirname(__file__)
sys.path.append(curr_dir)

from pdf_utilities import extract_text, select_text, invert_select_text
from dtype_conversions import str_to_float
from constants import expense_categories


class OCBCStatement:
    '''
    CLASS OBJECT for Singapore OCBC Credit Card Statement.
    input: filepath, to pdf file of credit card statement
    '''
    def __init__(self, filepath):
        self.filepath = filepath
        self.expense_categories = [ex for ex in expense_categories if ex != "Credit Card"]
    
    
    def get_statement_date(self):
        '''
        FUNCTION to get the statement date
        output: statement date in datetime format
        '''
        try:
            text = extract_text(self.filepath)
            date = select_text(text, "TOTAL MINIMUM DUE\n", "\n")
            return datetime.strptime(date, '%d-%m-%Y')
        except Exception as e:
            print(e)
    
    
    def get_transactions(self):
        '''
        FUNCTION to read transactions in statement
        output: dataframe with columns: Date, Description, Amount, Balance
        '''
        try:
            text = extract_text(self.filepath)
            
            # select transactions in same currency
            start1 = "LAST MONTH\'S BALANCE\n"
            end1 = "SUBTOTAL\n"
            subtext = select_text(text, start1, end1)
            
            # remove page-by-page header
            start2 = "\nOCBC Bank"
            end2 = "TRANSACTION DATE\nDESCRIPTION\nAMOUNT (SGD)\n"
            transactions = invert_select_text(subtext, start2, end2)
            
            # split by newline
            data = transactions.split("\n")
            data = [d for d in data if d] # remove empty lines
            subtotal = data[-1]
            data = data[:-1]
            
            # concatenate one record, one row
            for ii, x in enumerate(data):
                if '/' in x and x[x.find("/")-2:x.find("/")].isnumeric() and x[x.find("/")+1:x.find("/")+3].isnumeric():
                    idx = ii
                else:
                    data[idx] += " " + x
                    data[ii] = ''
            data = [d for d in data if d] # remove empty lines
            
            dates = [x[x.find("/")-2:x.find("/")+3] for x in data]
            sdate = self.get_statement_date()
            for ii, date in enumerate(dates):
                dd, mm = int(date[0:2]), int(date[3:])
                if mm > sdate.month:
                    dates[ii] = datetime(sdate.year-1, mm, dd)
                else:
                    dates[ii] = datetime(sdate.year, mm, dd)
            
            description, amount = [], []
            for ii, x in enumerate(data):
                # if contains parenthesis: credit
                if x.find("(") >= 0 and x.find(")") >= 0 and x[x.find("(")+1:x.find("(")+2].isnumeric():
                    amount.append(str_to_float(x[x.find("(")+1:x.find(".")+3]))
                    description.append(x[x.find(".")+4:x.rfind(")")].replace(' SINGAPORE SGP',''))
                # otherwise: debit
                else:
                    amount.append(-1*str_to_float(x[x.find("/")+4:x.find(".")+3]))
                    description.append(x[x.find(".")+4:].replace(' SINGAPORE SGP',''))
            
            # concatenate as a dataframe and append to master
            data = np.array((dates, description, amount)).T
            df = pd.DataFrame(columns = ['Date','Description','Amount'], data = data)
            
            df["Category"] = (df["Amount"].astype("category").cat.remove_categories(df["Amount"]).cat.add_categories(self.expense_categories))
            return df
            
        except Exception as e:
            print(e)

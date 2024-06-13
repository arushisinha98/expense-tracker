import os
import sys
from datetime import datetime
import pandas as pd
import numpy as np

curr_dir = os.path.dirname(__file__)
sys.path.append(curr_dir)

from dtype_conversions import str_to_float
from pdf_utilities import extract_text, select_text, invert_select_text
from constants import expense_categories

from decouple import config
FD = config('FD')

class DBSStatement:
    '''
    CLASS OBJECT for Singapore Bank (DBS) Statement.
    input: filepath, to pdf file of bank statement
    '''
    def __init__(self, filepath):
        self.filepath = filepath
    
    
    def get_balance(self):
        '''
        FUNCTION to read end-of-statement balance (in SGD)
        output: balance, as a numerical value
        '''
        try:
            text = extract_text(self.filepath)
            balance = select_text(text, "Total: SGD Equivalent", "\nSummary of Currency Breakdown")
            return str_to_float(balance)
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
            start1 = "Balance Brought Forward\n"
            end1 = "\nTotal Balance Carried Forward"
            subtext = select_text(text, start1, end1)
            
            # remove page-by-page balance carried/brought forward
            start2 = "Balance Carried Forward\n"
            end2 = "\nBalance Brought Forward"
            transactions = invert_select_text(subtext, start2, end2)
            
            # split by newline
            data = transactions.split("\n")
            start_balance = data[0]
            data = data[1:]
            
            for ii, x in enumerate(data):
                if 'SGD' in x: # remove balance carried forward
                    data[ii] = ''
                try: # convert to transaction date to datetime
                    data[ii] = datetime.strptime(x, '%d/%m/%Y')
                except:
                    pass # leave as text
            data = [d for d in data if d] # remove empty lines
            
            # get index range for each transaction
            first_idx = [ii for ii, x in enumerate(data) if isinstance(x, datetime)]
            first_idx.append(len(data))
            last_idx = [x-2 for x in first_idx if x >= 2]
            
            # concatenate text for full description
            description = []
            for ii in range(len(last_idx)):
                desc = ""
                for jj in range(first_idx[ii]+1, last_idx[ii]):
                    desc += str(data[jj]) + " "
                description.append(desc)
            
            # get dates, amount, balance for each transaction
            dates = [x for x in data if isinstance(x, datetime)]
            amount = [str_to_float(data[ii]) for ii in last_idx]
            balance = [str_to_float(data[ii+1]) for ii in last_idx]
            
            sign = []
            for ii, bal in enumerate(balance):
                if ii == 0:
                    sign.append(np.sign(bal - str_to_float(start_balance[3:])))
                else:
                    sign.append(np.sign(bal - balance[ii-1]))
            
            # concatenate as a dataframe and append to master
            data = np.array((dates, description, np.array(sign)*np.array(amount), balance)).T
            df = pd.DataFrame(columns = ['Date','Description','Amount','Balance'], data = data)
            df["Category"] = (df["Amount"].astype("category").cat.remove_categories(df["Amount"]).cat.add_categories(expense_categories))
            return df
            
        except Exception as e:
            print(e)


class FDStatement:
    '''
    CLASS OBJECT for Singapore Bank (DBS) Fixed Deposit (FD) Statement.
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
            datetext = select_text(text, "Account Summary as at ", "\n")
            return datetime.strptime(datetext, '%d %b %Y')
        except Exception as e:
            print(e)
    
    
    def get_balance(self):
        '''
        FUNCTION to read end-of-statement balance (in SGD)
        output: balance, as a numerical value
        '''
        try:
            text = extract_text(self.filepath)
            balance = select_text(text, "Fixed Deposit\nTotal: SGD Equivalent", "Account")
            return str_to_float(balance)
        except Exception as e:
            print(e)
    
    
    def get_transactions(self):
        '''
        FUNCTION to read the total balance (in SGD)
        output: dataframe with columns: Date, Balance
        '''
        try:
            new_df = pd.DataFrame(columns = ["Date", "Balance"], data = [[self.get_date(), self.get_balance()]])
            new_df["Source"] = "DBS - FD"
            return new_df
        except Exception as e:
            print(e)


class SRSStatement:
    '''
    CLASS OBJECT for Singapore Bank (DBS) Supplementary Retirement Scheme (SRS) Statement.
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
            datetext = select_text(text, "Account Summary as at ", "\n")
            return datetime.strptime(datetext, '%d %b %Y')
        except Exception as e:
            print(e)
    
    
    def get_balance(self):
        '''
        FUNCTION to read end-of-statement balance (in SGD)
        output: balance, as a numerical value
        '''
        try:
            text = extract_text(self.filepath)
            balance = select_text(text, "Supplementary Retirement Scheme Account", "Account")
            return str_to_float(balance)
        except Exception as e:
            print(e)
    
    
    def get_transactions(self):
        '''
        FUNCTION to read the total balance (in SGD)
        output: dataframe with columns: Date, Balance
        '''
        try:
            new_df = pd.DataFrame(columns = ["Date", "Balance"], data = [[self.get_date(), self.get_balance()]])
            new_df["Source"] = "DBS - SRS"
            if self.add_FD():
                add_df = FDStatement(self.filepath).get_transactions()
                return new_df.append(add_df)
            return new_df
        except Exception as e:
            print(e)
    
    
    def add_FD(self):
        '''
        FUNCTION to check if the statement also contains information on SRS balance
        output: boolean
        '''
        try:
            text = extract_text(self.filepath)
            return FD in text
        except Exception as e:
            print(e)

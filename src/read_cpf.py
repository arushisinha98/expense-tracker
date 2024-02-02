import fitz
import os
from datetime import datetime
import pandas as pd
import numpy as np

from pdf_utilities import extract_text, select_text, invert_select_text
from dtype_conversions import str_to_float
from constants import expense_categories


class CPFStatement:
    '''
    CLASS OBJECT for Singapore Bank (DBS) Statement.
    input: filepath, to pdf file of bank statement
    '''
    def __init__(self, filepath):
        self.filepath = filepath
    
    
    def get_account_year(self):
        try:
            text = extract_text(self.filepath)
            date = select_text(text, "Yearly Statement of Account for ", "\n")
            return date
            
        except Exception as e:
            print(e)
    
    
    def get_transactions(self):
        '''
        FUNCTION to read transactions in statement
        output: dataframe with columns: Date, Description, Amount, Balance
        '''
        try:
            text = extract_text(self.filepath)
            print(text)
            year = self.get_account_year()
            print(year)
            
            # select table content
            start1 = "MediSave\nAccount ($)\n"
            end1 = "\nSee Appendix"
            subtext = select_text(text, start1, end1)
            
            # remove page-by-page balance carried/brought forward
            transactions = invert_select_text(subtext, "ARUSHI SINHA", start1)
            
            # split by newline
            data = transactions.split("\n")
            # data = data[:-3]
            ii, max_ii = 0, len(data)
            
            while ii < max_ii:
                try:
                    data[ii] = datetime.strptime(data[ii]+f" {year}", '%d %b %Y')
                    ii += 1
                except:
                    if data[ii] == "CON":
                        data.pop(ii+1)
                        data.pop(ii+1)
                        max_ii -= 2
                    ii += 1
            
            data = np.reshape(data, (int(len(data)/5), 5))
            df = pd.DataFrame(columns = ["Date", "Code", "OA", "SA", "MA"], data = data)
            df[["OA","SA","MA"]] = df[["OA","SA","MA"]].applymap(str_to_float)
            df["Balance"] = df.sum(axis = 1)
            
            balance_index = list(df[df["Code"] == "BAL"].index)
            for ii, code in enumerate(df["Code"]):
                if code != "BAL":
                    last_balance = sum([f < ii for f in balance_index])-1
                    df.iloc[ii, len(df.columns)-1] = df["Balance"][ii-1] + df["Balance"][ii]
            
            return df[["Date","Balance"]]
            
        except Exception as e:
            print(e)

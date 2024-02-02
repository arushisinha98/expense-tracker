from datetime import datetime
import pandas as pd
import numpy as np


class IBKRStatement:
    '''
    CLASS OBJECT for Interactive Brokers (IBKR) Statement.
    download instructions: Statements >> MTM Summary >> Monthly
    '''
    def __init__(self, filepath):
        self.filepath = filepath
        
    def get_transactions(self):
        '''
        FUNCTION to read the total balance (in SGD)
        output: dataframe with columns: Date, Balance
        '''
        try:
            df = pd.read_csv(f"{self.filepath}", on_bad_lines = 'skip')
            date_range = df['Field Value'][df['Field Name'] == "Period"].values[0]
            end_date = datetime.strptime(date_range[date_range.find("-")+2:], '%B %d, %Y')
            balance = float(df['Field Value'][df['Field Name'] == "Ending Value"].values[0])
            new_df = pd.DataFrame(columns = ["Date", "Balance"], data = [[end_date, balance]])
            return new_df
        except Exception as e:
            print(e)

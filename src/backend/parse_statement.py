import pandas as pd
import numpy as np
from datetime import datetime
import re
from abc import ABC, abstractmethod

from src.backend.read_utilities import parse_pdf, parse_image, parse_llama


class Statement(ABC):
    def __init__(self, filepath, parse_method):
        self.type = ''
        self.upload_date = datetime.now()
        self.last_update = self.upload_date
        self.filepath = filepath
        self.parse_method = parse_method
        self.fulltext = ''
        self.transactions = []

    @abstractmethod
    def read_statement(self, parse_method):
        pass
        
    @abstractmethod
    def parse_statement(self):
        pass

    def get_transactions(self):
        return self.transactions

    def update_transactions(self, df):
        self.transactions = df.to_dict('records')
        self.last_update = datetime.now()

    def get_last_update(self):
        return self.last_update

    def save_transactions(self):
        filepath = self.filepath
        if "." not in filepath:
            filepath += '.csv'
        elif not filepath.endswith('.csv'):
            filepath = filepath[:filepath.rfind(".")] + '.csv'
        df = pd.DataFrame(self.transactions)
        df.to_csv(filepath, index = False)


class ParsePDF(Statement):
    def __init__(self, filepath, parse_method):
        super().__init__(filepath, parse_method)

    def read_statement(self, parse_method):
        if parse_method == "image OCR":
            self.parse_method = "image OCR"
            content = parse_image(self.filepath)
            self.fulltext = content
        else:
            self.parse_method = "llama-parse"
            content = parse_llama(self.filepath)
            self.fulltext = content
    
    def parse_statement(self):
        try:
            lines = self.fulltext.split('\n')
            for line in lines:
                line = line.replace('=', '')
                transaction = self.parse_line(line)
                if transaction:
                    self.transactions.append(transaction)
        except Exception as e:
            print(f"Error parsing PDF: {e}")
        
    @abstractmethod
    def parse_line(self, line, parse_method):
        pass


def adjust_year(transaction_date, statement_date):
    current_year = statement_date.year
    if transaction_date.month > statement_date.month:
        # if statement date is in the new year
        return transaction_date.replace(year=current_year - 1)
    else:
        return transaction_date.replace(year=current_year)
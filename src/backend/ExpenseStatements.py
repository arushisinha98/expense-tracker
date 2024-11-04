import pandas as pd
import numpy as np
from datetime import datetime
import re
from abc import ABC, abstractmethod
from dateutil.parser import parse
from decimal import Decimal

from src.backend.read_utilities import parse_pdf, parse_image, parse_llama


class ExpenseStatement(ABC):
    def __init__(self, filepath, parse_method):
        self.type = "expense"
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


class ParsePDF(ExpenseStatement):
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
        

class SCExpense(ParsePDF):
    def __init__(self, filepath, parse_method):
        super().__init__(filepath, parse_method)
        self.regex_patterns = {
            "image OCR": (
                r'(\d{2}\s[A-Za-z]{3})\s+'        # Transaction date
                r'(\d{2}\s[A-Za-z]{3})\s+'        # Post date
                r'(.*?\s+Transaction Ref \d+)\s+' # Description
                r'(\d+\.\d{2}(?:\s*CR)?)'         # Amount
                ),
            "llama-parse": (
                r'\|\s*(\d{1,2}\s[A-Za-z]{3})\s*'
                r'\|\s*(\d{1,2}\s[A-Za-z]{3})?\s*'
                r'\|\s*(.*?)\s*'
                r'\|\s*(\d+\.\d{2}(?:\s*CR)?)\s*\|'
                )
            }
        self.read_statement(parse_method)
        self.statement_date = self.get_statement_date()
        self.parse_statement()
        
    def parse_line(self, line):
        match = re.search(
            self.regex_patterns[self.parse_method], line)
        if match:
            try:
                transaction_date = datetime.strptime(match.group(1), '%d %b')
                description = match.group(3)
                amount = match.group(4)
                
                if 'CR' in amount:
                    amount = -Decimal(amount.replace('CR', '').strip())
                else:
                    amount = Decimal(amount)
                
                transaction_date = adjust_year(
                    transaction_date, self.statement_date
                    )
                
                return {
                    'Date': transaction_date,
                    'Description': description,
                    'Amount': amount,
                    'Category': '',
                    'Comments': ''
                }
            except (ValueError, IndexError) as e:
                print(f"Error reading line '{line}': {str(e)}")
                return None
        return None

    def get_statement_date(self):
        header = (
            r'Statement\s*Date\s*:?\s*(\d{1,2}\s*[A-Za-z]{3}\s*\d{4})'
            )
        match = re.search(header, self.fulltext.replace('*',''))
        statement_date = datetime.strptime(match.group(1), '%d %b %Y')
        return statement_date


class HSBCExpense(ParsePDF):
    def __init__(self, filepath, parse_method):
        super().__init__(filepath, parse_method)
        self.regex_patterns = {
            "image OCR": (
                r'(\d{1,2}\s?[A-Za-z]{3})\s*'  # Post date
                r'(\d{1,2}\s?[A-Za-z]{3})\s*'  # Transaction date
                r'(.+?)'                       # Description
                r'(?:\s+(\d+\.\d{2}(?:\s*CR)?))?$' # Amount (optional)
                ),
            "llama-parse": (
                r'\|\s*(\d{2}\s[A-Za-z]{3})\s*'
                r'\|\s*(\d{2}\s[A-Za-z]{3})\s*'
                r'\|\s*(.*?)\s*'
                r'\|\s*(\d+\.\d{2}(?:\s*CR)?)\s*\|'
                )
            }
        self.read_statement(parse_method)
        self.statement_date = self.get_statement_date()
        self.parse_statement()

    def parse_line(self, line):
        match = re.search(
            self.regex_patterns[self.parse_method],line
            )
        if match:
            try:
                try:
                    transaction_date = datetime.strptime(match.group(2), '%d%b')
                except ValueError:
                    try:
                        transaction_date = datetime.strptime(match.group(2), '%d %b')
                    except ValueError:
                        transaction_date = None
                description = match.group(3)
                amount = match.group(4) if match.group(4) else '0.00'
                
                if amount:
                    if 'CR' in amount:
                        amount = -Decimal(amount.replace('CR', '').strip())
                    else:
                        amount = Decimal(amount.strip())
                        
                transaction_date = adjust_year(
                    transaction_date, self.statement_date
                    )
                
                return {
                    'Date': transaction_date,
                    'Description': description,
                    'Amount': amount,
                    'Category': '',
                    'Comments': ''
                }
            except (ValueError, IndexError) as e:
                print(f"Error reading line '{line}': {str(e)}")
                return None
        return None

    def get_statement_date(self):
        header = (
            r'(Statement From:?\s*\d{2}\s[A-Z]{3}\s\d{4}\s+to\s+)'
            r'(\d{2}\s[A-Z]{3}\s\d{4})'
            )
        match = re.search(header, self.fulltext)
        statement_date = datetime.strptime(match.group(2), '%d %b %Y')
        return statement_date
        

def adjust_year(transaction_date, statement_date):
    current_year = statement_date.year
    if transaction_date.month > statement_date.month:
        # if statement date is in the new year
        return transaction_date.replace(year=current_year - 1)
    else:
        return transaction_date.replace(year=current_year)

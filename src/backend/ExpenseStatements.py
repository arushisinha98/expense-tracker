import pandas as pd
import numpy as np
from datetime import datetime
import re
from abc import ABC, abstractmethod
from dateutil.parser import parse
from decimal import Decimal


class ExpenseStatement(ABC):
    def __init__(self, filepath, fulltext):
        self.type = "expense"
        self.upload_date = datetime.now()
        self.file_path = filepath
        self.fulltext = fulltext
        self.transactions = []
        
    @abstractmethod
    def parse_statement(self):
        pass

    @abstractmethod
    def match_identifiers(self, identifiers):
        pass

    def get_transactions(self):
        return self.transactions

    def add_classification(self, index, category):
        if 0 <= index < len(self.transactions):
            self.transactions[index]['Category'] = category

    def add_comment(self, index, comment):
        if 0 <= index < len(self.transactions):
            self.transactions[index]['Comments'] = comment


class PDFExpenseStatement(ExpenseStatement):
    def __init__(self, filepath, fulltext):
        super().__init__(filepath, fulltext)

    def parse_statement(self):
        try:
            lines = self.fulltext.split('\n')
            for line in lines:
                line = line.replace('=', '')
                transaction = self.parse_line(line)
                if transaction:
                    self.transactions.append(transaction)
        except Exception as e:
            print(f"Error parsing PDF: {str(e)}")

    def match_identifiers(self, identifiers):
        text = self.fulltext
        return all(identifier in text for identifier in identifiers)
        
    @abstractmethod
    def parse_line(self, line):
        pass
        

class SCStatement(PDFExpenseStatement):
    def __init__(self, filepath, fulltext):
        super().__init__(filepath, fulltext)
        self.identifiers = ["ARUSHI SINHA", "-2340"]
        self.statement_date = self.get_statement_date()
        self.regex_patterns = (
            r'(\d{2}\s[A-Z][a-z]{2})\s+'  # First date
            r'(\d{2}\s[A-Z][a-z]{2})\s+'  # Second date
            r'(.*?)\s+'                   # Description
            r'(Transaction Ref \d+)\s+'   # Transaction Ref
            r'(\d+\.\d{2}(?:\s*CR)?)'     # Amount
        )
        self.parse_statement()
        
    def parse_line(self, line):
        match = re.match(self.regex_patterns, line)
        if match:
            try:
                transaction_date = datetime.strptime(match.group(1), '%d %b')
                description = match.group(3)
                amount = match.group(5)
                
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
            except (ValueError, IndexError):
                return (f"Error reading line '{line}': {str(e)}")
        return None

    def get_statement_date(self):
        date = None
        for line in self.fulltext.split('\n'):
            if "Statement Date" in line:
                date = datetime.strptime(
                    line.split(':')[1].strip(), '%d %b %Y'
                    )
                break
            
        if not date:
            raise ValueError("Could not find statement date")
        
        self.statement_date = date
        return self.statement_date


class HSBCStatement(PDFExpenseStatement):
    def __init__(self, filepath, fulltext):
        super().__init__(filepath, fulltext)
        self.identifiers = ["ARUSHI SINHA", "-2726"]
        self.statement_date = self.get_statement_date()
        self.regex_patterns = (
            r'(\d{1,2}\s?[A-Za-z]{3})\s*'  # First date
            r'(\d{1,2}\s?[A-Za-z]{3})\s*'  # Second date
            r'(.+?)'                       # Description
            r'(?:\s+(\d+\.\d{2}(?:\s*CR)?))?$' # Amount (optional)
            )
        self.parse_statement()

    def parse_line(self, line):
        match = re.search(self.regex_patterns, line)
        if match:
            try:
                try:
                    transaction_date = datetime.strptime(match.group(1), '%d%b')
                except ValueError:
                    try:
                        transaction_date = datetime.strptime(match.group(1), '%d %b')
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
            except (ValueError, IndexError):
                return (f"Error reading line '{line}': {str(e)}")
        return None

    def get_statement_date(self):
        header = (
            r'(Statement From \d{2}\s[A-Z]{3}\s\d{4} to )'
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

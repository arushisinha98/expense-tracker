from datetime import datetime
import re
from decimal import Decimal

from src.backend.parse_statement import ParsePDF, adjust_year


class ExampleExpense(ParsePDF):
    def __init__(self, filepath, parse_method):
        super().__init__(filepath, parse_method)
        self.type = "expense"
        # for each parse_method, add regex pattern to identify transactions of interest in the statement
        self.regex_patterns = {
            "image OCR": (
                r'(\d{1,2}\s?[A-Za-z]{3})\s*'  # Transaction date
                r'(.+?)'                       # Description
                r'(?:\s+(\d+\.\d{2}?))?$'      # Amount
                ),
            "llama-parse": ('')
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
                    transaction_date = datetime.strptime(match.group(1), '%d %b')
                except ValueError:
                    transaction_date = None
                description = match.group(2)
                amount = match.group(3) if match.group(3) else '0.00'
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
        header = ('') # add regex pattern to identify statement date
        match = re.search(header, self.fulltext)
        statement_date = datetime.strptime(match, '%d %b %Y')
        return statement_date
    

class ExampleBalance(ParsePDF):
    def __init__(self, filepath, parse_method):
        super().__init__(filepath, parse_method)
        self.type = "balance"
        # for each parse_method, add regex pattern to identify transactions of interest in the statement
        self.regex_patterns = {
            "image OCR": (
                r'(\d{1,2}\s?[A-Za-z]{3})\s*'  # Date
                r'(?:\s+(\d+\.\d{2}?))?$'      # Balance
                ),
            "llama-parse": ('')
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
                    transaction_date = datetime.strptime(match.group(1), '%d %b')
                except ValueError:
                    transaction_date = None
                balance = match.group(2) if match.group(2) else '0.00'
                balance = Decimal(balance.strip())
                        
                transaction_date = adjust_year(
                    transaction_date, self.statement_date
                    )
                
                return {
                    'Date': transaction_date,
                    'Balance': balance,
                    'Comments': ''
                }
            except (ValueError, IndexError) as e:
                print(f"Error reading line '{line}': {str(e)}")
                return None
        return None

    def get_statement_date(self):
        header = ('') # add regex pattern to identify statement date
        match = re.search(header, self.fulltext)
        statement_date = datetime.strptime(match, '%d %b %Y')
        return statement_date
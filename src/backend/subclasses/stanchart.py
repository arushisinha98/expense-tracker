from datetime import datetime
import re
from decimal import Decimal

from src.backend.parse_statement import ParsePDF, adjust_year


class StanChartExpense(ParsePDF):
    def __init__(self, filepath, parse_method):
        super().__init__(filepath, parse_method)
        self.type = "expense"
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
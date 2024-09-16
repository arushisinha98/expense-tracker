import re
from datetime import datetime


def str_to_date(date_string):
    '''
    FUNCTION to convert DD MMM YYYY format to datetime
    input: date_string, string as a date, e.g. 10 Dec 2023
    output: date, in datetime format
    '''
    date = datetime.strptime(date_string, '%d %b %Y')
    return date


def str_to_float(dollars_string):
    '''
    FUNCTION to convert string to numerical value
    input: dollars_string, input string
    output: dollars, numerical value as float
    '''
    if "-" in dollars_string:
        mult = -1
    else:
        mult = 1
    dollars = re.sub(r'[^0-9.]', "", dollars_string)
    return mult*float(dollars)


def float_to_str(dollars):
    '''
    FUNCTION to convert numerical value to string with 1000s separator and 2 d.p.
    input: dollars, numerical value as float
    output: dollars_string, output string
    '''
    return "{:,.2f}".format(dollars)


def redact_text(dollars_string):
    '''
    FUNCTION to redact the numbers in a string and replace with 'X'
    input: dollars_string, input string
    output: redact_string, redacted string
    '''
    redact_string = re.sub(r'\d', "X", dollars_string)
    return redact_string

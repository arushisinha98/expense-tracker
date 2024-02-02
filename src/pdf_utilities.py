import fitz
import os
from datetime import datetime


def extract_text(filepath):
    '''
    FUNCTION to extract text from PDF file.
    input: filepath, to pdf file
    output: text, pdf file contents as a string
    '''
    try:
        doc = fitz.open(filepath)
        text = ""
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(e)


def select_text(text, before, after):
    '''
    FUNCTION to select text between two snippets in string
    input:
    - text, input contents as a string
    - before, snippet of text before selection
    - after, snippet of text after selection
    output: selected text between before and after snippets
    '''
    assert len(text) > 0
    try:
        start = text.find(before) + len(before)
        subtext = text[start:]
        end = subtext.find(after)
        return text[start:start+end]
    except Exception as e:
        print(e)


def invert_select_text(text, before, after):
    '''
    FUNCTION to invert selection of select_text function
    input:
    - text, input contents as a string
    - before, snippet of text before non-selection
    - after, snippet of text after non-selection
    output: selected text that does not include snippet between before and after
    '''
    assert len(text) > 0
    try:
        if text.find(before) < 0 and text.find(after) < 0:
            return text
        elif text.find(before) == 0 and text.find(after) >= 0:
            subtext = text[text.find(after) + len(after):]
            return invert_select_text(subtext, before, after)
        else:
            subtext1 = text[:text.find(before)]
            subtext2 = text[text.find(after) + len(after):]
            return invert_select_text(subtext1 + subtext2, before, after)
    except Exception as e:
        print(e)

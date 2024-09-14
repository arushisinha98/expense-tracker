import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import re
import PyPDF2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
from pdf2image import convert_from_path
from dateutil.parser import parse
from decimal import Decimal


def read_pdf(filepath):
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            fulltext = ""
            for page in pdf_reader.pages:
                fulltext += page.extract_text()
        return fulltext if fulltext.strip() else None
    except Exception as e:
        print(f"Error reading PDF: {str(e)}")
        return None


def read_image(filepath):
    try:
        with open(filepath, 'rb') as file:
            # Convert PDF to image
            images = convert_from_path(filepath, 300)
            fulltext = ""
            for img in images:
                # Perform OCR
                text = pytesseract.image_to_string(img)
                fulltext += text + "\n"
        return fulltext
    except Exception as e:
        print(f"Error reading image: {str(e)}")
        return None

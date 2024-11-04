import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import re
import PyPDF2
import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
from pdf2image import convert_from_path
from dateutil.parser import parse
from decimal import Decimal

from dotenv import load_dotenv
load_dotenv()
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader


def parse_pdf(filepath):
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            fulltext = ""
            for page in pdf_reader.pages:
                fulltext += page.extract_text()
        return fulltext if fulltext.strip() else None
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None


def parse_image(filepath):
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
        print(f"Error reading image: {e}")
        return None


def parse_llama(filepath):
    try:
        prompt = "The document provided is a statement of transactions. \
Cleanly extract the relevant text and tables from the statement. \
Extract the line that includes the statement date or period. \
Extract the transactions as a table with fields including transaction date, \
posting date, description, and amount. If the amount was credited, add the \
suffix 'CR' immediately following the amount. \
Extract all other text that is relevant to the statement, account, or transactions."
        parser = LlamaParse(
            result_type = "markdown",
            parsing_instruction = prompt,
            skip_diagonal_text = True,
            do_not_unroll_columns = True,
            use_vendor_multimodal_model = True,
            vendor_multimodal_model_name = "openai-gpt-4o-mini"
            )
        docs = SimpleDirectoryReader(
            input_files = [filepath],
            file_extractor = {".pdf": parser}
            ).load_data()
        fulltext = ""
        fulltext += "\n".join(docs[ii].text for ii in range(len(docs)))
        return fulltext
    except Exception as e:
        print(f"Error using llama-parse: {e}")
        return None

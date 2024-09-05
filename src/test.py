import os
import sys
from datetime import date
import pandas as pd
import streamlit as st
from decouple import config
MASTER_DIRECTORY = config('MASTER_DIRECTORY')

curr_dir = os.path.dirname(__file__)
sys.path.append(curr_dir)

from constants import expense_categories, tabs, converter
from app import README, MAIN


def main():
    print(f"MASTER DIRECTORY: {MASTER_DIRECTORY}")
    print(f"CURRENT DIRECTORY: {curr_dir}")


if __name__ == '__main__':
    main()
    MAIN()
    

import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime

# import from the root directory
rootDir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(rootDir)

from constants import expense_categories, tabs
from utilities import *


def uploader(border = True):
    '''
    FUNCTION to create data uploader with backend logic to process, extract, and save data from uploaded statements.
    '''
    
    with st.container(border = border):
        # file uploader for statements
        uploaded_file = st.file_uploader(
            "Upload a new statement",
            accept_multiple_files = False
            )
        
        if uploaded_file:
            if "file_upload" not in st.session_state:
                st.session_state["file_upload"] = uploaded_file



@st.cache_data
def initialize_data(tabletype):
    assert tabletype in ['Expense', 'Balance']
    
    try:
        if tabletype == 'Expense':
            df = pd.DataFrame(
                columns=["Date",
                         "Description",
                         "Amount",
                         "Category"]
                )
            df["Date"] = pd.to_datetime(df["Date"])
            df["Amount"] = df["Amount"].astype("float64")
        else:
            df = pd.DataFrame(columns=["Date",
                                       "Balance"]
                              )
            df["Date"] = pd.to_datetime(df["Date"])
            df["Balance"] = df["Balance"].astype("float64")
        return df.set_index("Date")
    except Exception as e:
        st.error(f"Error initializing data: {e}")
        return pd.DataFrame()


def tabulator(border = True):
    '''
    FUNCTION to create manual data tabulator with backend logic to save data.
    '''
    with st.container(border = border):
        col1, col2 = st.columns([1,2])
                    
        # radio: choose location tag
        with col1:
            country = st.radio("Choose a location tag",
                               list(tabs.keys()))
            tag = tabs[country]['tag']
        
        # radio: choose table type
        with col2:
            tabletype = st.radio("Choose a table type",
                                 ['Expense','Balance'])
            st.session_state["ManualTable"] = initialize_data(tabletype)


        # editable dataframe for manual entry
        if tabletype == 'Expense':
            edited = st.data_editor(
                st.session_state["ManualTable"],
                use_container_width = True,
                num_rows = 'dynamic',
                column_config = {
                    "Date": st.column_config.DateColumn(),
                    "Category": st.column_config.SelectboxColumn(
                        options = expense_categories
                        )
                    }
                )
        else:
            edited = st.data_editor(
                st.session_state["ManualTable"],
                use_container_width = True,
                num_rows = 'dynamic',
                column_config = {
                    "Date": st.column_config.DateColumn()
                    }
                )

        # text input: create filename
        filename = st.text_input("Create filename",
                                 placeholder = "e.g. HSBC/FEB-2024")
        if filename:
            bool, df = search_data(filename)
            if bool:
                st.write("⚠️ A file with this name already exists.")
                st.session_state["SubmitError"] = True

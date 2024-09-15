import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Union
import re

from constants import expense_categories, tabs

sys.path.append('..')
from utilities import DataDirectory, get_absolute_path

sys.path.append(get_absolute_path('backend'))
from read_utilities import read_pdf, read_image
from ExpenseStatements import SCStatement, HSBCStatement


def uploader(upload_folder, tabletype, border = True):
    '''
    FUNCTION to create data uploader with backend logic to process,
    extract, and save data from uploaded statements.
    '''
    with st.container(border=border):
        
        # file uploader for statements (one file at a time only)
        uploaded_file = st.file_uploader(
            "Upload a new statement",
            accept_multiple_files=False
        )
        
        # initialize session state variables
        if "uploaded_file" not in st.session_state:
            st.session_state["uploaded_file"] = None
        if "uploaded_dataframe" not in st.session_state:
            st.session_state["uploaded_dataframe"] = None
        if "upload_processed" not in st.session_state:
            st.session_state["upload_processed"] = False
        
        # check if a new file has been uploaded
        if uploaded_file and uploaded_file != st.session_state["uploaded_file"]:
            st.session_state["uploaded_file"] = uploaded_file
            filepath = f"{upload_folder}/{uploaded_file.name}"
            
            DataDirectory.insert_file(
                content = uploaded_file.getbuffer(),
                destination = filepath
                )

            # create statement object
            st.session_state["statement_object"] = create_statement(filepath)
            st.session_state["uploaded_dataframe"] = pd.DataFrame(
                st.session_state["statement_object"].get_transactions()
                )

        # display data editor
        if st.session_state["uploaded_dataframe"] is not None:
            editable_df = show_editable_df(
                st.session_state["uploaded_dataframe"],
                num_rows='fixed'
                )
            st.session_state["editabled_df"] = editable_df
            
            submit_button = st.button(
                "Save",
                disabled = disable_save(editable_df),
                key = "upload_save")
            
            if submit_button:
                st.session_state["statement_object"].update_transactions(editable_df)
                st.session_state["statement_object"].save_transactions()
                
            

def tabulator(upload_folder, tabletype, border = True):
    '''
    FUNCTION to create manual data tabulator with backend logic to save data.
    '''
    with st.container(border = border):
        st.session_state["tabulated_dataframe"] = initialize_data(tabletype)
        editable_df = show_editable_df(
            st.session_state["tabulated_dataframe"],
            num_rows='dynamic'
            )

        # text input: create filename
        filename = st.text_input("Create filename",
                                 placeholder = "e.g. HSBC/FEB-2024")
                
        if filename:
            main_bool, df = search_data(filename)
            if main_bool:
                st.write("⚠️ A file with this name already exists.")
                st.session_state["SubmitError"], main_bool = True, True
            if filename.count("/") < 1:
                st.write("⚠️ One sub-directory must be created.")
                st.session_state["SubmitError"], main_bool = True, True
            elif filename.count("/") > 1:
                st.write("⚠️ Only sub-directory may be created.")
                st.session_state["SubmitError"], main_bool = True, True

        # get filepath to save manual data
        if tabletype and filename and not main_bool:
            st.session_state["SubmitError"] = False
            subdir = f"{upload_folder}/{filename[:filename.find('/')]}/"
            if not os.path.exists(subdir):
                os.mkdir(subdir)
            filepath = subdir + filename[filename.find('/')+1:] + '.csv'

        submit_button = st.button("Save",
                                  disabled = disable_save(editable_df),
                                  key = "manual_save")
        if submit_button and st.session_state["SubmitError"]==False:
            editable_df.reset_index().to_csv(filepath, index = True)
            st.write(f"Data uploaded to `~/data/{tag}/{filename}.csv`")


def create_statement(filepath: str) -> Union[
        SCStatement,
        HSBCStatement,
        None]:
    content = read_image(filepath)
    checks = {
        "Standard Chartered": r"Standard Chartered Bank",
        "HSBC": r"HSBC",
    }
    
    for bank, pattern in checks.items():
        if re.search(pattern, content, re.IGNORECASE):
            if bank == "Standard Chartered":
                return SCStatement(filepath, content)
            elif bank == "HSBC":
                return HSBCStatement(filepath, content)
    return None


@st.cache_data
def initialize_data(tabletype):
    if tabletype == 'Expense':
        df = pd.DataFrame(
            columns=["Date",
                     "Description",
                     "Amount",
                     "Category",
                     "Comments"]
            )
        df["Date"] = pd.to_datetime(df["Date"])
        df["Amount"] = df["Amount"].astype("float64")
    else:
        df = pd.DataFrame(columns=["Date",
                                   "Balance",
                                   "Comments"]
                          )
        df["Date"] = pd.to_datetime(df["Date"])
        df["Balance"] = df["Balance"].astype("float64")
    return df.set_index("Date")


def show_editable_df(df, num_rows):
    column_config = {}
    
    if 'Date' in df.columns:
        column_config['Date'] = st.column_config.DateColumn()
    
    if 'Category' in df.columns:
        column_config['Category'] = st.column_config.SelectboxColumn(
            options=expense_categories
        )

    if 'Amount' in df.columns:
        column_config['Amount'] = st.column_config.NumberColumn(
            'Amount',
            min_value=-99999,
            max_value=99999,
            step=0.01,
            format="%.2f"
        )
    
    editable_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows=num_rows,
        column_config=column_config
    )
    return editable_df
        

def disable_save(editable_df,
                 optional_cols = ["Comments"]):
    if editable_df.empty:
        return True
    if "Category" in editable_df.columns:
        if any(cat not in expense_categories for cat in editable_df["Category"]):
            return True
    if "Amount" in editable_df.columns:
        if any(amt == 0 for amt in editable_df["Amount"]):
            st.write("Ensure all expenses were read correctly from statement.")
    mandatory_cols = list(set(editable_df.columns) - set(optional_cols))
    if editable_df[mandatory_cols].isnull().all().any():
        return True
    return editable_df[mandatory_cols].isnull().any().any()

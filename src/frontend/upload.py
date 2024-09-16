import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Union
import re

from constants import expense_categories, tabs
from utilities import DataDirectory, get_absolute_path
from format_utilities import create_annotations

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
        if "statement_object" not in st.session_state:
            st.session_state["statement_object"] = None
        
        # check if a new file has been uploaded
        if uploaded_file and uploaded_file != st.session_state["uploaded_file"]:
            filename = uploaded_file.name
            filetype = uploaded_file.name[uploaded_file.name.rfind("."):]

            # if processed .csv has been saved, retrieve and show
            processed_file = filename[:filename.rfind(".")]+".csv"
            if DataDirectory.search_directory(processed_file):
                st.write("A file with this name has already been processed.")
                st.session_state["statement_object"] = create_statement(
                    f"{upload_folder}/{uploaded_file.name}"
                    )
                retrieved_df = pd.read_csv(
                    f"{upload_folder}/{processed_file}",
                    index_col = 0
                    )
                st.session_state["statement_object"].update_transactions(retrieved_df)
                st.session_state["uploaded_dataframe"] = retrieved_df

            else:
                st.session_state["uploaded_file"] = uploaded_file
                filepath = f"{upload_folder}/{filename}"

                # insert file into directory
                DataDirectory.insert_file(
                    content = uploaded_file.read(),
                    destination = filepath
                    )

                # create statement object and read transactions
                st.session_state["statement_object"] = create_statement(filepath)
                st.session_state["uploaded_dataframe"] = pd.DataFrame(
                    st.session_state["statement_object"].get_transactions()
                    )

        # display data editor
        if st.session_state["uploaded_dataframe"] is not None:
            if tabletype == 'Expense':
                create_annotations(
                    st.session_state["uploaded_dataframe"],
                    column = "Amount",
                    threshold = 0,
                    labels = ["Payments", "Expenses"]
                    )
                
            editable_df = show_editable_df(
                st.session_state["uploaded_dataframe"],
                num_rows='dynamic'
                )
            st.session_state["editable_dataframe"] = editable_df
            
            submit_button = st.button("Save",
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

        # initialize session state variables
        if "SubmitError" not in st.session_state:
            st.session_state["SubmitError"] = None
        st.session_state["tabulated_dataframe"] = initialize_data(tabletype)

        # display data editor
        editable_df = show_editable_df(
            st.session_state["tabulated_dataframe"],
            num_rows='dynamic'
            )

        # create unique filename
        filename = st.text_input(
            "Create filename for tabulated data.",
            placeholder = f"e.g. {datetime.now().month}-{datetime.now().year}"
            )
        if filename and len(filename) > 0:
            while DataDirectory.search_directory(filename):
                st.write("⚠️ A file with this name already exists.")
                st.session_state["SubmitError"] = True
            st.session_state["SubmitError"] = False

        # save data in chosen directory
        if st.session_state["SubmitError"] == False:
            filename = filename[:filename.rfind('.')]+'.csv'
            filepath = f"{upload_folder}/{filename}"

        submit_button = st.button("Save",
            disabled = disable_save(editable_df),
            key = "manual_save")
        
        if submit_button:
            editable_df.reset_index().to_csv(filepath, index = False)
            st.write(f"Data uploaded to `~/data/{upload_folder}/{filename}.csv`")


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

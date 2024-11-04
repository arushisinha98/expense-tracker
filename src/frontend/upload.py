import streamlit as st
import pandas as pd
from typing import Union
from datetime import date, datetime

from src.constants import expense_categories
from src.utilities import DataDirectory
from src.format_utilities import create_annotations

from src.backend.read_utilities import parse_pdf, parse_image, parse_llama
from src.backend.subclasses import *


def auto_upload(upload_folder, tabletype, border = True):
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
            st.session_state["uploaded_file"] = uploaded_file
            filename = uploaded_file.name

            # if processed .csv has been saved, retrieve and show
            processed_file = filename[:filename.rfind(".")]+".csv"
            found = DataDirectory.search_directory(filename)
            processed = DataDirectory.search_directory(processed_file)
            if found and processed:
                st.write("A file with this name has already been processed.")
                st.session_state["statement_object"] = create_statement(found)
                retrieved_df = DataDirectory.retrieve_file(processed)
                st.session_state["statement_object"].update_transactions(retrieved_df)
                st.session_state["uploaded_dataframe"] = retrieved_df

            else:
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
                tabletype
                )
            st.session_state["editable_dataframe"] = editable_df
            
            submit_button = st.button("Save",
                disabled = disable_save(editable_df),
                key = "upload_save")
            
            if submit_button:
                st.session_state["statement_object"].update_transactions(editable_df)
                st.session_state["statement_object"].save_transactions()


def manual_upload(upload_folder, tabletype, border = True):
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
            tabletype
            )

        # create unique filename
        filename = st.text_input(
            "Create filename for tabulated data.",
            placeholder = "e.g. {ACCOUNT_NAME}" + f"-{datetime.now().month}-{datetime.now().year}"
            )
        if filename and len(filename) > 0:
            if "." in filename:
                filename = filename[:filename.rfind(".")]+".csv"
            else:
                filename = filename+".csv"
            file_exists = DataDirectory.search_directory(filename)
            if file_exists:
                st.warning("⚠️ A file with this name already exists.")
                st.session_state["SubmitError"] = True
            else:
                st.session_state["SubmitError"] = False
                st.session_state["filepath"] = f"{upload_folder}/{filename}"

        submit_button = st.button("Save",
            disabled = disable_save(editable_df),
            key = "manual_save")
        
        if submit_button and st.session_state["SubmitError"] == False:
            editable_df.reset_index().to_csv(
                st.session_state["filepath"], index = False
                )
            st.write(f"`{filename}` successfully uploaded")


# @st.cache_data
def initialize_data(tabletype):
    if tabletype == 'Expense':
        df = pd.DataFrame(
            columns=["Date",
                     "Description",
                     "Amount",
                     "Category",
                     "Comments"]
            )
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        df["Amount"] = df["Amount"].astype("float64")
    elif tabletype == 'Balance':
        df = pd.DataFrame(columns=["Date",
                                   "Balance",
                                   "Comments"]
                          )
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        df["Balance"] = df["Balance"].astype("float64")
    else:
        return pd.DataFrame()
    return df.set_index("Date")


def show_editable_df(df, tabletype):
    if tabletype == 'Expense':
        editable_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows='dynamic',
            column_config={
                "Date": st.column_config.DateColumn(
                    min_value=date(1900, 1, 1),
                    max_value=date(datetime.now().year, datetime.now().month, datetime.now().day),
                    format="MM/DD/YYYY",
                    step=1
                ),
                "Category": st.column_config.SelectboxColumn(
                    options=expense_categories
                ),
                "Amount": st.column_config.NumberColumn(
                    min_value=-99999,
                    max_value=99999,
                    step=0.01,
                    format="%.2f"
                )
            },
            hide_index=True,
        )
    elif tabletype == 'Balance':
        editable_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows='dynamic',
            column_config={
                "Date": st.column_config.DateColumn(
                    min_value=date(1900, 1, 1),
                    max_value=date(2100, 12, 31),
                    format="MM/DD/YYYY",
                    step=1
                ),
                "Balance": st.column_config.NumberColumn(
                    min_value=-99999,
                    max_value=99999,
                    step=0.01,
                    format="%.2f"
                )
            },
            hide_index=True,
        )
    else:
        editable_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows='dynamic',
            hide_index=True,
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


def create_statement(filepath: str) -> Union[
        StanChartExpense,
        HSBCExpense,
        None]:
    content = parse_llama(filepath)
    checks = {
        "Standard Chartered": ["-2340"],
        "HSBC": ["-2726"],
    }
    
    for account, identifiers in checks.items():
        if all(identifier in content for identifier in identifiers):
            if account == "Standard Chartered":
                print("Creating StanChartExpense statement object")
                return StanChartExpense(filepath, "llama-parse")
            elif account == "HSBC":
                print("Creating HSBCExpense statement object")
                return HSBCExpense(filepath, "llama-parse")
    return None
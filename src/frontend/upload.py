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
    FUNCTION to create data uploader with backend logic to process,
    extract, and save data from uploaded statements.
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
            
            # if file found, load processed dataframe
            main_bool, df = search_data(uploaded_file.name)
            if main_bool:
                if "upload_data" not in st.session_state:
                    st.session_state["upload_data"] = df
                if "preprocessed" not in st.session_state:
                    st.session_state["preprocessed"] = True



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


def disable_save(edited):
    # no rows added
    bool1 = edited.shape[0] == 0
    # incomplete/unfilled cells
    bool2 = any([pd.isnull(
        edited.loc[ix, col]) for ix in edited.index for col in edited.columns])
    if bool1 or bool2:
        return True
    else:
        return False


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
        if country and tabletype and filename and not main_bool:
            st.session_state["SubmitError"] = False
            if filename.count("/") == 1:
                subdir = f"{rootDir}/data/{tag}/{filename[:filename.find('/')]}/"
                if not os.path.exists(subdir):
                    os.mkdir(subdir)
                filepath = subdir + filename[filename.find('/')+1:] + '.csv'
            else:
                filepath = os.getcwd() + f"/data/{tag}/{filename}.csv"
    
        submit_button = st.button("Submit",
                                  disabled = disable_save(edited),
                                  key = "ManualUpload")
        if submit_button and st.session_state["SubmitError"]==False:
            edited.reset_index().to_csv(filepath, index = True)
            st.write(f"Data uploaded to `~/data/{tag}/{filename}.csv`")

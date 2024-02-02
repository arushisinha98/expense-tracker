import os
import sys

curr_dir = os.path.dirname(__file__)
sys.path.append(curr_dir)

import numpy as np
import pandas as pd
import streamlit as st
from annotated_text import annotated_text
from constants import account_names, expense_categories
from dtype_conversions import float_to_str
from formatting import format_table
from uploader import clear_directory, search_data, process_upload, completed, save_data


def page1():
    st.header("Data")
    st.caption("Add monthly bank, credit card, or investment statements to the database.")
    
    # file uploader for statements
    uploaded_file = st.file_uploader("Upload a new statement", accept_multiple_files = False)
    
    # display Expense Categories in expander
    with st.expander("Expense Categories"):
        st.write(f"""Categories are listed in `constants.py`.
        *{expense_categories}*
        """)
    
    if uploaded_file:
        if "file_upload" not in st.session_state:
            st.session_state["file_upload"] = uploaded_file
        
        # if file found, load processed dataframe
        bool, df = search_data(uploaded_file.name)
        if bool:
            if "upload_data" not in st.session_state:
                st.session_state["upload_data"] = df
            if "preprocessed" not in st.session_state:
                st.session_state["preprocessed"] = True
        
        # if file not found, create processed dataframe and save in relevant data folder
        else:
            bytes_data = uploaded_file.read()
            with open(f"data/uploads/{uploaded_file.name}", 'wb') as f:
                f.write(bytes_data)
            statement = process_upload(f"{uploaded_file.name}", bytes_data)
            if statement:
                df = statement.get_transactions()
                if "upload_data" not in st.session_state:
                    st.session_state["upload_data"] = df
                if "preprocessed" not in st.session_state:
                    st.session_state["preprocessed"] = False
        
        # show dataframe
        if "upload_data" in st.session_state:
            df = st.session_state["upload_data"]
            if "Amount" in df.columns:
                annotated_text((float_to_str(sum(df["Amount"][df["Amount"] < 0])), "Outgoing"), "\t",
                               (float_to_str(sum(df["Amount"][df["Amount"] >= 0])), "Incoming"))
            df = format_table(df)
            if st.session_state["preprocessed"]: # not editable if already preprocessed
                classified_df = st.data_editor(df, num_rows = 'fixed', disabled = True, use_container_width = True)
            else:
                classified_df = st.data_editor(df, num_rows = 'fixed', disabled = ('Date','Amount','Balance'), use_container_width = True)
                save = st.button("Submit", disabled = completed(classified_df)==False)
                if save:
                    save_data(classified_df, uploaded_file.name)
                    
        else:
            st.write(f"⚠️ ERROR: Could not read file")
        
        # reset session_state for new upload
        st.session_state.pop("file_upload")
        if "upload_data" in st.session_state:
            st.session_state.pop("upload_data")
            st.session_state.pop("preprocessed")


def page3():
    st.header("📱 Calculator")
    st.caption("Manually fill out account values to compute total net worth in USD.")

    #@st.cache_data
    def initialize_data() -> pd.DataFrame:
        df = pd.DataFrame(columns = ["Account","Currency","Raw Value"])
        df["Account"], df["Currency"] = list(account_names.keys()), list(account_names.values())
        df["Raw Value"] = np.zeros((len(df),1))
        
        df["Currency"] = df["Currency"].astype("category")
        df["Raw Value"] = df["Raw Value"].astype("float64")
        return df

    with st.form("form"):
        st.caption("⏰ Estimated time: 10 minutes")
        edited = st.data_editor(initialize_data(), use_container_width = True, num_rows = 'dynamic')
        submit_button = st.form_submit_button("Calculate")

    converter = [0.75,1]
    if submit_button:
        total = [x*converter[edited["Currency"][ii] == "USD"] for ii, x in enumerate(edited["Raw Value"])]
        st.write(f"Total in USD: ${float_to_str(sum(total))}")

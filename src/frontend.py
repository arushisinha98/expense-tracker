import os
import sys

curr_dir = os.path.dirname(__file__)
sys.path.append(curr_dir)

from decouple import config
MASTER_DIRECTORY = config('MASTER_DIRECTORY')

import numpy as np
import pandas as pd
import streamlit as st
from annotated_text import annotated_text

from constants import account_names, expense_categories, credit_categories
from dtype_conversions import float_to_str
from format_utilities import format_table
from upload_utilities import clear_directory, search_data, process_upload, completed, save_data


def uploader():
    st.header("📤 Upload Data")
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
            
            
def tabulator():
    st.caption("OR Manually tabulate data.")
    
    # date, description, amount, category
    @st.cache_data
    def initialize_data() -> pd.DataFrame:
        df = pd.DataFrame(columns = ["Date","Description","Amount","Category"])
        df["Date"] = df["Date"].astype("datetime64")
        df["Amount"] = df["Description"].astype("float64")
        df["Category"] = df["Category"].astype("category")
        return df
    
    with st.form(key = "manual_form"):
        df_editor = st.data_editor(initialize_data(),
                                   use_container_width = True, num_rows = 'dynamic', hide_index = True,
                                   column_config = {"Date": st.column_config.DateColumn(),
                                                    "Category": st.column_config.SelectboxColumn(options = expense_categories)}
        )
        
        """
        option = st.selectbox("", ("🇸🇬 Singapore", "🇺🇸 United States"),
                              index = None,
                              placeholder = "Choose a classification tag ...",
                              label_visibility = "collapsed",
        )
        st.write(option)
        
        submit_button = st.form_submit_button("Submit", disabled = option is None)
        """
        submit_button = st.form_submit_button("Submit")

def calculator(master_df = pd.DataFrame()):
    st.header("⚖️ Calculator")
    st.caption("Manually fill out account values to compute total net worth in USD.")

    @st.cache_data
    def initialize_data() -> pd.DataFrame:
        df = pd.DataFrame(columns = ["Account","Currency","Raw Value"])
        df["Account"], df["Currency"] = list(account_names.keys()), list(account_names.values())
        df["Raw Value"] = np.zeros((len(df),1))
        df["Currency"] = df["Currency"].astype("category")
        df["Raw Value"] = df["Raw Value"].astype("float64")
        return df

    with st.form(key = "calculator_form"):
        st.caption("⏰ Estimated time: 10 minutes")
        edited = st.data_editor(initialize_data(), use_container_width = True, num_rows = 'dynamic')
        submit_button = st.form_submit_button("Calculate")

    converter = [0.75,1]
    if submit_button:
        total = [x*converter[edited["Currency"][ii] == "USD"] for ii, x in enumerate(edited["Raw Value"])]
        st.write(f"Total in USD: ${float_to_str(sum(total))}")


def show_cards(country):
    assert country in ["SG", "US"]
    
    try:
        if country == "SG":
            cc1, cc2, cc3 = st.tabs(["HSBC Revolution","OCBC 90°N","Standard Chartered Smart"])
            with cc1:
                ccards, ctext = st.columns([1, 3])
                with ccards:
                    st.image("images/hsbc-revolution.jpg", width = 175)
                with ctext:
                    st.caption("No Annual Fee | 3.25% Foreign Currency Transaction Fee")
                    st.caption("4 miles per S\$1 up to S\$1,000/month, 0.4 miles per S$1 thereafter")
                    st.caption("5:2 KrisFlyer Miles Conversion, S\$43.60 Annual Transfer Fee")
            with cc2:
                ccards, ctext = st.columns([1, 3])
                with ccards:
                    st.image("images/ocbc-90nmastercard.png", width = 175)
                with ctext:
                    st.caption("S\$196.20 Annual Fee | 3.25% Foreign Currency Transaction Fee + Mastercard Fees (~1%)")
                    st.caption("1.3 miles per S\$1 Local Spend, 2.1 miles per S\$1 Foreign Spend")
                    st.caption("1:1 KrisFlyer / Flying Blue Miles Conversion, S\$25 Conversion Fee")
                
            with cc3:
                ccards, ctext = st.columns([1, 3])
                with ccards:
                    st.image("images/sc-smart.jpg", width = 175)
                with ctext:
                    st.caption("No Annual Fee | 3.5% Foreign Currency Transaction Fee")
                    st.caption("19.2 points per S\$1 on BUS/MRT, 1.6 points per S\$1 otherwise")
                    st.caption("320 points = S\$1 | 1.015:1 KrisFlyer Miles Conversion, S\$26.75 Conversion Fee")
                    
        else:
            cc1, cc2 = st.tabs(["Chase United Gateway","Bank of America Travel Rewards"])
            with cc1:
                ccards, ctext = st.columns([1, 3])
                with ccards:
                    st.image("images/chase-unitedgateway.png", width = 175)
                with ctext:
                    st.caption("No Annual Fee | No Foreign Currency Transaction Fee")
                    st.caption("2 miles per \$1 on United® purchases, gas stations, local transit")
                    st.caption("1 mile per \$1 otherwise")
            with cc2:
                ccards, ctext = st.columns([1, 3])
                with ccards:
                    st.image("images/boa-travelrewards.jpg", width = 175)
                with ctext:
                    st.caption("No Annual Fee | No Foreign Currency Transaction Fee")
                    st.caption("1.5 points per \$1 on all purchases")
                         
    except Exception as e:
        print(e)

from datetime import date
import os
import streamlit as st
from streamlit_card import card
from annotated_text import annotated_text
import sys
import numpy as np
import altair as alt
import pandas as pd

curr_dir = os.path.dirname(__file__)
sys.path.append(curr_dir)

from constants import expense_categories
from format_utilities import format_table, horizontal_bar, vertical_bar, local_css
from upload_utilities import clear_directory, search_data, process_upload, completed, save_data
from dtype_conversions import float_to_str, redact_text
from compile_utilities import compile_statements, category_table, balance_table

from frontend import uploader, tabulator, calculator, show_cards

data_tab, sg_tab, us_tab, summary_tab = st.tabs(["Upload", "Singapore", "United States", "Calculator"])

# clear data in uploads folder
clear_directory()

# initialize master_df (to be used in calculator page)
master_df = pd.DataFrame()


with data_tab:
    st.header("📤 Upload Data")
    
    # display Expense Categories in expander
    with st.expander("Expense Categories"):
        st.write(f"""Categories are listed in `constants.py`.
        *{expense_categories}*
        """)
        
    st.caption("Add monthly bank, credit card, or investment statements to the database.")
    uploader(border = True)
    
    st.caption("OR Manually tabulate data.")
    tabulator(border = True)


with sg_tab:
    st.header("🇸🇬 Singapore")
    
    # create a checkbox to redact values
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col6:
        redact = st.checkbox("**REDACT**", key = "redact_SG")
    
    # container 1: expense tracker
    with st.container(border = True):
        date_col, summary_col = st.columns([1, 1])
        with date_col:
            period = st.date_input('Select Period',
                                   value = (date(date.today().year, 1, 1), date.today()),
                                   max_value = date.today(),
                                   format = "YYYY/MM/DD")
            df = compile_statements('SG', period)
        
        # display total spend & total investment annotation
        if not df is None:
            table = category_table(df, period)
            with summary_col:
                st.write("""<h1> </h1>""", unsafe_allow_html = True)
                spend = table.sum(axis = 1).iloc[0] - table['Investment'][0]
                invest = table['Investment'][0]
                
                if redact:
                    annotated_text(
                        (redact_text(float_to_str(spend)), "Spend"), "\t",
                        (redact_text(float_to_str(invest)), "Invest"))
                else:
                    annotated_text(
                        (float_to_str(spend), "Spend"), "\t",
                        (float_to_str(invest), "Invest"))
                               
            # horizontal bar of expense
            table.drop('Investment', axis = 1, inplace = True)
            chart = horizontal_bar(table, redact)
            st.altair_chart(chart, use_container_width = True)
            
            # dataframe of transactions, filterable by category
            with st.expander("View Details"):
                modify = st.checkbox("Filter by Category")
                if not modify:
                    st.dataframe(df[["Date","Source","Description","Amount","Category"]]\
                                 .loc[df["Category"].isin(expense_categories)]\
                                 .reset_index(drop = True), use_container_width = True)
                else:
                    filter_categories = st.multiselect("↳ Select", expense_categories)
                    st.dataframe(df[["Date","Source","Description","Amount","Category"]]\
                                 .loc[df["Category"].isin(filter_categories)]\
                                 .reset_index(drop = True), use_container_width = True)
    
    # container 2: details of active credit cards
    show_cards("SG", redact)
    
    # container 3: account balance
    with st.container(border = True):
        # account balance chart
        df = compile_statements('SG', (date(1998,10,10), date.today()))
        series = balance_table(df, (date(1998,10,10), date.today()))
        pivot_df = pd.pivot_table(series, values = 'Balance', index = ['Date'],
                                  columns = ['Source'], aggfunc = "mean")
        
        chart = vertical_bar(pivot_df, redact)
        st.altair_chart(chart, use_container_width = True)
        
        # dataframe of account balances over time
        with st.expander("View Details"):
            st.dataframe(pivot_df, use_container_width = True)
        
    # take last value in each column and add to master_df
    save_amounts = dict()
    for col in pivot_df.columns:
        save_amounts[col] = pivot_df[col].ffill().iloc[-1]
    save_df = pd.DataFrame.from_dict(save_amounts, orient = 'index', columns = ["Raw Value"])
    save_df["Currency"] = "SGD"
    master_df = master_df.append(save_df)
    

with us_tab:
    st.header("🇺🇸 United States")
    
    # create a checkbox to redact values
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col6:
        redact = st.checkbox("**REDACT**", key = "redact_US")
    
    show_cards("US", redact)


with summary_tab:
    calculator(master_df)

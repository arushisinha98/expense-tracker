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
from format_utilities import format_table, horizontal_bar, local_css
from upload_utilities import clear_directory, search_data, process_upload, completed, save_data
from dtype_conversions import float_to_str
from compile_utilities import compile_statements, category_table, balance_table

from frontend import uploader, tabulator, calculator, show_cards

readme_tab, sg_tab, us_tab, summary_tab = st.tabs(["Upload", "Singapore", "United States", "Calculator"])


# clear data in uploads folder
clear_directory()

# initialize master_df
master_df = pd.DataFrame()

with readme_tab:
    uploader()

with sg_tab:
    st.header("🇸🇬 Singapore")
    
    with st.container(border = True):
        
        date_col, summary_col = st.columns([1, 1])
        with date_col:
            period = st.date_input('Select Period',
                                   value = (date(date.today().year, 1, 1), date.today()),
                                   max_value = date.today(),
                                   format = "YYYY/MM/DD")
                
            df = compile_statements('SG', period)
        
        if not df is None:
            # display total spend & total investment
            table = category_table(df, period)
            with summary_col:
                st.write("""<h1> </h1>""", unsafe_allow_html = True)
                annotated_text((float_to_str(table.sum(axis = 1).iloc[0] - table['Investment'][0]), "Spend"), "\t",
                               (float_to_str(table['Investment'][0]), "Invest"))
                               
            # horizontal bar of expense
            table.drop('Investment', axis = 1, inplace = True)
            chart = horizontal_bar(table)
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
    
    show_cards("SG")
    
    with st.container(border = True):
        # account balance chart
        df = compile_statements('SG', (date(1998,10,10), date.today()))
        series = balance_table(df, (date(1998,10,10), date.today()))
        st.bar_chart(series, x = "Date", y = "Balance", color = "Source", width = 10)
        table_df = pd.pivot_table(series, values = 'Balance', index = ['Date'],
                                  columns = ['Source'], aggfunc = "mean")
               
        # dataframe of accounts
        with st.expander("View Details"):
            st.dataframe(table_df, use_container_width = True)
    
    
with us_tab:
    st.header("🇺🇸 United States")
    show_cards("US")

with summary_tab:
    calculator()

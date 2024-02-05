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

from frontend import uploader, tabulator, calculator

readme_tab, sg_tab, us_tab, summary_tab = st.tabs(["Upload", "Singapore", "United States", "Calculator"])


# clear data in uploads folder
clear_directory()

# initialize master_df
master_df = pd.DataFrame()

with readme_tab:
    uploader()
    tabulator()

with sg_tab:
    st.header("🇸🇬 Singapore")
    
    # quick select year-to-date or lifetime date range
    button1, button2, button3, space = st.columns([1,1,1,2.5])
    local_css("style.css")
    with button1:
        last_month = st.button("Last Month")
    with button2:
        ytd = st.button("Year-to-date")
    with button3:
        all = st.button("Lifetime")
    
    # get user input date or override with quick select
    date_col, summary_col = st.columns([1, 1])
    with date_col:
        if last_month:
            mm = date.today().month
            if mm == 1:
                value = (date(date.today().year-1, 12, 1), date(date.today().year, 1, 1))
            else:
                value = (date(date.today().year, date.today().month-1, 1), date(date.today().year, date.today().month, 1))
        elif ytd:
            value = (date(date.today().year, 1, 1), date.today())
        elif all:
            value = (date(1998,10,10), date.today())
        else: # default: mtd
            value = (date(date.today().year, date.today().month, 1), date.today())
        period = st.date_input('Select Period',
                               value = value,
                               max_value = date.today(),
                               format = "YYYY/MM/DD")
        df = compile_statements('SG', period)
    
    # if dataframe is compiled, show horizontal bar of expense categories and spend/invest annotation
    if not df is None:
        table = category_table(df, period)
        with summary_col:
            st.write("""<h1> </h1>""", unsafe_allow_html = True)
            annotated_text((float_to_str(table.sum(axis = 1).iloc[0] - table['Investment'][0]), "Spend"), "\t",
                           (float_to_str(table['Investment'][0]), "Invest"))
        table.drop('Investment', axis = 1, inplace = True)
        chart = horizontal_bar(table)
        st.altair_chart(chart, use_container_width = True)
    
    st.caption("CREDIT CARDS")
    cc1, cc2, cc3 = st.tabs(["HSBC Revolution","OCBC 90°N","Standard Chartered Smart"])
    with cc1:
        ccards, ctext = st.columns([1, 3])
        with ccards:
            st.image("images/hsbc-revolution.jpg",
                     caption = "HSBC Revolution", width = 175)
        with ctext:
            st.caption("No Annual Fee | 3.25% Foreign Currency Transaction Fee")
            st.caption("4 miles per S\$1 up to S\$1,000/month, 0.4 miles per S$1 thereafter")
            st.caption("5:2 KrisFlyer Miles Conversion, S\$43.60 Annual Transfer Fee")
    with cc2:
        ccards, ctext = st.columns([1, 3])
        with ccards:
            st.image("images/ocbc-90nmastercard.png",
                     caption = "OCBC 90°N", width = 175)
        with ctext:
            st.caption("S\$196.20 Annual Fee | 3.25% Foreign Currency Transaction Fee + Mastercard fees (~1%)")
            st.caption("1.3 miles per S\$1 Local Spend, 2.1 miles per S\$1 Foreign Spend")
            st.caption("1:1 KrisFlyer / Flying Blue Miles Conversion, S\$25 Conversion Fee")
        
    with cc3:
        ccards, ctext = st.columns([1, 3])
        with ccards:
            st.image("images/sc-smart.jpg",
                     caption = "Standard Chartered Smart", width = 175)
        with ctext:
            st.caption("No Annual Fee | 3.5% Foreign Currency Transaction Fee")
            st.caption("19.2 points per S\$1 on BUS/MRT, 1.6 points per S\$1 otherwise")
            st.caption("320 points = S\$1 | 1.015:1 KrisFlyer Miles Conversion, S\$26.75 Conversion Fee")
        
                
    # account balance chart and table
    st.subheader("Account Balance", divider = "gray")
    df = compile_statements('SG', (date(1998,10,10), date.today()))
    series = balance_table(df, (date(1998,10,10), date.today()))
    st.bar_chart(series, x = "Date", y = "Balance", color = "Source", width = 10)
    table_df = pd.pivot_table(series, values = 'Balance', index = ['Date'],
                              columns = ['Source'], aggfunc = "mean")
    st.dataframe(table_df, use_container_width = True)
    
    # append table_df to master_df
    master_df = master_df.append(table_df)
    
with us_tab:
    st.header("🇺🇸 United States")
    
    st.subheader("Credit Card Spending", divider = "gray")
    ccard, cspend = st.columns([1, 3])
    with ccard:
        st.image("images/boa-travelrewards.jpg",
                 caption = "Bank of America Travel Rewards", width = 175)
        st.image("images/chase-unitedgateway.png",
                 caption = "Chase United Gateway", width = 175)
    
    st.subheader("Transfers", divider = "gray")

with summary_tab:
    calculator(master_df)

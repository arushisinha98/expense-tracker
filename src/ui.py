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
from formatting import format_table, horizontal_bar, local_css
from uploader import clear_directory, search_data, process_upload, completed, save_data
from dtype_conversions import float_to_str
from compile_spend import compile_statements, category_table, balance_table

from frontend import page1, page3

readme_tab, sg_tab, us_tab, summary_tab = st.tabs(["Upload", "Singapore", "United States", "Calculator"])


# clear data in uploads folder (staging)
clear_directory()

with readme_tab:
    page1()

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
    ccard1, ccard2, ccard3 = st.columns([1, 1, 1])
    with ccard1:
        st.image("images/hsbc-revolution.jpg",
                 caption = "HSBC Revolution", width = 175)
    with ccard2:
        st.image("images/ocbc-90nmastercard.png",
                 caption = "OCBC 90°N", width = 175)
    with ccard3:
        st.image("images/sc-smart.jpg",
                caption = "Standard Chartered Smart", width = 175)
                
    # account balance chart and table
    st.subheader("Account Balance", divider = "gray")
    df = compile_statements('SG', (date(1998,10,10), date.today()))
    series = balance_table(df, (date(1998,10,10), date.today()))
    st.bar_chart(series, x = "Date", y = "Balance", color = "Source", width = 10)
    table_df = pd.pivot_table(series, values = 'Balance', index = ['Date'],
                       columns = ['Source'], aggfunc = "mean")
    st.dataframe(table_df, use_container_width = True)
    
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
    page3()

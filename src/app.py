from datetime import date
import os
import sys

curr_dir = os.path.dirname(__file__)
sys.path.append(curr_dir)

import numpy as np
import pandas as pd
import streamlit as st
from annotated_text import annotated_text
import altair as alt

from constants import expense_categories, tabs
from format_utilities import horizontal_bar, vertical_bar
from upload_utilities import clear_directory, completed
from dtype_conversions import float_to_str, redact_text
from compile_utilities import compile_statements, category_table, balance_table
from frontend import uploader, tabulator, calculator, show_cards


def MAIN():
    # create tabs
    tab_names = ["Upload"] + list(tabs.keys()) + ["Calculator"]
    tab_content = st.tabs(tab_names)

    # clear data in uploads folder
    clear_directory()

    # initialize master_df (to be used in calculator page)
    master_df = pd.DataFrame()

    with tab_content[0]:
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
        
    
    for ii, country in enumerate(tabs.keys()):
        with tab_content[ii+1]:
            st.header(f"{country}")
            
            # create a checkbox to redact $$ values
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col6:
                redact = st.checkbox("**REDACT**", key = f"redact{ii}")
            
            # expense tracker
            with st.container(border = True):
                date_col, summary_col = st.columns([1, 1])
                with date_col:
                    period = st.date_input('Select Period',
                                           value = (date(date.today().year, 1, 1), date.today()),
                                           max_value = date.today(),
                                           format = "YYYY/MM/DD",
                                           key = f"date_input{ii}")
                    df = compile_statements(country, period)
                # display total spend & investment annotation
                if not df is None and df.shape[0] > 0:
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
                    
            # details of active credit cards
            show_cards(country, redact)
            
            # account balance
            with st.container(border = True):
                # vertical bar of balance
                df = compile_statements(country, (date(1998,10,10), date.today()))
                
                if not df is None and df.shape[0] > 0:
                    series = balance_table(df, (date(1998,10,10), date.today()))
                    pivot_df = pd.pivot_table(series, values = 'Balance', index = ['Date'],
                                              columns = ['Source'], aggfunc = "mean")
                    
                    chart = vertical_bar(pivot_df, redact)
                    st.altair_chart(chart, use_container_width = True)
                    
                    # dataframe of accounts
                    
                    with st.expander("View Details"):
                        st.dataframe(pivot_df, use_container_width = True)
                        
                    # take last value in each column and add to master_df
                    save_amounts = dict()
                    for col in pivot_df.columns:
                        save_amounts[col] = pivot_df[col].ffill().iloc[-1]
                    save_df = pd.DataFrame.from_dict(save_amounts, orient = 'index', columns = ["Raw Value"])
                    save_df["Currency"] = tabs[country]['currency']
                    master_df = master_df.append(save_df)
    
    
    with tab_content[-1]:
        calculator(master_df)
    



def README():
    '''
    FUNCTION to create a README viewer of the frontend in when some baseline assertions have failed.
    '''
    try:
        README, Example = st.tabs(["README", "Example"])
        
        with README:
            st.header("Welcome!")
            st.write("Thanks for checking out my personal project on GitHub. Before you start using my source code to build your own financial planning app, you'll need to make a few adjustments. Once you have completed the checklist, refresh your browser window.")
            
            # prepare constants.py file
            st.checkbox("**Open `constants.py` and initialize these three variables: `expense_categories`, `tabs`, and `converter`.**", key = "check1")
            
            with st.container(border = True):
                placeholder_expense_categories = ['Groceries','Dining','Transport','Entertainment','Investment','Taxes / Bills','Rent','Others']

                st.write("`expense_categories` is a list categories to help you classify your expenses and/or outgoing transactions. Here is an example to get you started:")
                st.write(placeholder_expense_categories)
                
                placeholder_tabs = {'United States': {'tag': "US", 'currency': "USD"}}
                
                st.write("`tabs` is a dictionary that is used to organize the backend data and frontend visualizations by currency and/or location. The dictionary requires details including the name of the tab, its short-hand tag, and its associated currency. Use the following structure:")
                st.write(placeholder_tabs)
                
                placeholder_converter = {"USD": 1}
                
                st.write("`converter` is a dictionary with currencies as keys and the conversion rate to a common base currency as values. Be sure to include _all_ currencies that were declared in `tabs`. Here is an example to go with the one above:")
                st.write(placeholder_converter)
            
            # prepare data directory
            st.checkbox("**Prepare the data directory to match `tabs`.**", key = "check2")
            
            with st.container(border = True):
                st.write("All the data for your app will be in `../data/`. Within this folder, make sure that there exists a subdirectory for uploads as well as one for _each_ tag that was initialized in `tabs`. Here is an example of what it should look like:")
                st.write(['../data/uploads/','../data/US/'])
            
            # some notes
            st.write("*Note that you will need to configure the logic for uploading and saving data from your bank, credit card, and investment statements. However, once you have completed the above steps, the manual data entry should work just fine!*")
            
        
        with Example:
            st.write("Here are some static screenshots of what the financial app looks like when it is up and running.")
            
            with st.container(border = True):
                st.image('screenshots/upload.png')
                st.caption("Tab organization and a place to upload or manually enter data.")
                
            with st.container(border = True):
                st.image('screenshots/expense-example.png')
                st.caption("The expense tracker, showing spend in each category.")
                
            with st.container(border = True):
                st.image('screenshots/balance-example.png')
                st.caption("The balance viewer, showing account balances over time.")
                
            
    except Exception as e:
        print(e)

import os
import sys
from datetime import date
import pandas as pd
import streamlit as st

from constants import expense_categories, tabs
from utilities import DataDirectory, get_absolute_path

rootDir = get_absolute_path('..')
frontendDir = get_absolute_path('frontend')
backendDir = get_absolute_path('backend')

sys.path.append(frontendDir)
from upload import uploader, tabulator


def MAIN():
    # create tabs
    tab_names = ["Upload"] + list(tabs.keys())
    tab_content = st.tabs(tab_names)

    with tab_content[0]:
        st.header("📤 Upload Data")
        
        # display Expense Categories in expander
        with st.expander("Expense Categories"):
            st.write(f"""Categories are listed in `constants.py`.
            *{expense_categories}*
            """)
        
        col1, col2 = st.columns([1,1])           
        # radio: choose statement type
        with col1:
            tabletype = st.radio(
                label = "Choose a statement type and a directory to save the data.",
                options = ['Expense','Balance'],
                index = None
                )
        
        # radio: choose directory
        with col2:
            select = st.selectbox(
                label = "Select a directory to save the data.",
                placeholder = "Choose a directory",
                options = DataDirectory.print_tree_structure(),
                index = None,
                label_visibility = 'hidden')

        if select:
            upload_folder = DataDirectory.get_full_path(select)
            st.caption("Add monthly bank, credit card, or investment statements to the database.")
            uploader(upload_folder, tabletype)
            
            st.caption("OR Manually tabulate data.")
            tabulator(upload_folder, tabletype)



def README():
    '''
    FUNCTION to create a README viewer of the frontend when some baseline assertions have failed.
    '''
    try:
        README, Example = st.tabs(["README", "Example"])

        with README:
            st.header("HELLO!")
            st.subheader("If you're seeing this, your app isn't quite ready.")
            st.write("Before you start using my source code to build your own financial planning app, you'll need to make a few adjustments. Here's a basic checklist. Once you have completed these items, refresh your browser window.")

            # prepare constants.py file
            st.checkbox("**Open `constants.py` and initialize `expense_categories`, `tabs`, and `converter`.**", key = "check1")

            with st.container(border = True):
                placeholder_expense_categories = ['Groceries','Dining','Transport','Entertainment','Investment','Taxes / Bills','Rent / Mortgage','Others']

                st.write("`expense_categories` is a *LIST* of categories to help you classify your expenses and/or outgoing transactions. Here is an example to get you started:")
                st.write(placeholder_expense_categories)

                placeholder_tabs = {'United States': {'tag': "US", 'currency': "USD"},
                                    'Singapore': {'tag': "SG", 'currency': "SGD"}}

                st.write("`tabs` is a *DICTIONARY* that is used to organize the backend data and frontend visualizations by currency and/or location. The dictionary minimally requires details including the name of the tab, its short-hand tag, and its associated currency. Use the following structure:")
                st.write(placeholder_tabs)

                placeholder_converter = {"USD": 1, "SGD": 0.74}

                st.write("`converter` is a *DICTIONARY* with currencies as keys and the conversion rate to a common base currency as values. Be sure to include _all_ currencies that were declared in `tabs`. Here is an example to go with the one above:")
                st.write(placeholder_converter)

            # prepare data directory
            st.checkbox("**Prepare the data directory.**", key = "check2")

            with st.container(border = True):
                st.write("All the data for your app will be in `../data/`. Within this folder, make sure that there exists a subdirectory for uploads as well as one for _each_ tag that was initialized in `tabs`. Here is an example of what it should look like:")
                st.write(['../data/US/','../data/SG/'])
                st.write("Feel free to add subdirectories.")

            # some notes
            st.write("*Note that you will need to configure the logic for automatically saving data from your bank, credit card, and/or investment statements. However, once you have completed the above steps, the manual data entry should work just fine!*")

        with Example:
            st.write("Here are some screenshots of what the financial app looks like when it is up and running.")

            with st.container(border = True):
                st.image('screenshots/upload.png')
                st.caption("**A place to upload or manually enter data.** Once you configure the logic for automatically saving data from your statements, they will appear here for you confirm and add to your database.")

            with st.container(border = True):
                st.image('screenshots/expense-example.png')
                st.caption("**An expense tracker, showing spend in each category.** You can click `View Details` to see a table of the transactions that took place within the selected period, which you can then filter by category.")

            with st.container(border = True):
                st.image('screenshots/balance-example.png')
                st.caption("**A balance viewer, showing account balances over time.** You can click `View Details` to see a table of your account balances at the end of each month. Missing data are forward filled by the last recorded balance of each account.")


    except Exception as e:
        print(e)
        

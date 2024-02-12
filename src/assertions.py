from datetime import datetime
import os
import sys
import streamlit as st

from decouple import config
MASTER_DIRECTORY = config('MASTER_DIRECTORY')

curr_dir = os.path.dirname(__file__)
sys.path.append(curr_dir)

from constants import expense_categories, tabs, converter


# check each tab has an associated currency
assert all(['currency' in list(value.keys()) for key, value in tabs.items()])
# check each currency is accounted for in converter
assert all(tab['currency'] in list(converter.keys()) for tab in tabs.values())

# check if data directory exists
assert os.path.exists(f"{MASTER_DIRECTORY}/data/")
# check data directory is organized by tab
assert all([os.path.exists(f"{MASTER_DIRECTORY}/data/{tab['tag']}/") for tab in tabs.values()])
# check data dirctory contains uploads folder
assert os.path.exists(f"{MASTER_DIRECTORY}/data/uploads/")

# check expense_categories is list
assert isinstance(expense_categories, list)



def README():
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
                st.image('../screenshots/upload.png')
                st.caption("Tab organization and a place to upload or manually enter data.")
                
            with st.container(border = True):
                st.image('../screenshots/expense-example.png')
                st.caption("The expense tracker, showing spend in each category.")
                
            with st.container(border = True):
                st.image('../screenshots/balance-example.png')
                st.caption("The balance viewer, showing account balances over time.")
                
            
    except Exception as e:
        print(e)

README()

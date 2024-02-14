import os
from datetime import datetime
import pandas as pd
import streamlit as st

from decouple import config
MASTER_DIRECTORY = config('MASTER_DIRECTORY')

from constants import expense_categories, tabs, converter
from dtype_conversions import float_to_str
from format_utilities import create_annotations, format_table, update_data_editor
from upload_utilities import search_data, process_upload, completed, save_data



def uploader(border = True):
    '''
    FUNCTION to create data uploader with backend logic to process, extract, and save data from uploaded statements.
    '''
    
    with st.container(border = border):
        # file uploader for statements
        uploaded_file = st.file_uploader("Upload a new statement", accept_multiple_files = False)
        
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
                else:
                    st.write("⚠️ ERROR: Could not process file contents")
            
            # show dataframe (either extracted or preprocessed)
            if "upload_data" in st.session_state:
                df = st.session_state["upload_data"]
                if "Amount" in df.columns:
                    create_annotations(df, column = "Amount", threshold = 0, labels = ["Outgoing", "Incoming"])
                df = format_table(df)
                # not editable if already preprocessed
                if st.session_state["preprocessed"]:
                    classified_df = st.data_editor(df, num_rows = 'fixed', disabled = True, use_container_width = True)
                else:
                    classified_df = st.data_editor(df, num_rows = 'fixed', disabled = ('Date','Amount','Balance'), use_container_width = True)
                    
                    # save in same directory as raw data file
                    save = st.button("Upload", disabled = completed(classified_df)==False, key = "AutoUpload")
                    if save:
                        save_data(classified_df, uploaded_file.name)
                        
            else:
                st.write("⚠️ ERROR: Could not read file")
        
            # reset session_state for new upload
            st.session_state.pop("file_upload")
            if "upload_data" in st.session_state:
                st.session_state.pop("upload_data")
                st.session_state.pop("preprocessed")
            
            
            
def tabulator(border = True):
    '''
    FUNCTION to create manual data tabulator with backend logic to save data.
    '''
    # TODO: update_data_editor to save latest iteration of manual table
    
    # initialize empty dataframe with columns: date, description, amount, category
    @st.cache_data
    def initialize_data() -> pd.DataFrame:
        df = pd.DataFrame(columns = ["Date","Description","Amount","Category"])
        df["Date"] = df["Date"].astype("datetime64")
        df["Amount"] = df["Amount"].astype("float64")
        return df.set_index("Date")
        
    if "ManualTable" not in st.session_state:
        st.session_state["ManualTable"] = initialize_data()
        
    if "SubmitError" not in st.session_state:
        st.session_state["SubmitError"] = False
    
    with st.container(border = border):
        col1, col2 = st.columns([1,1])
        
        # radio: choose location tag
        with col1:
            country = st.radio("Choose a location tag", list(tabs.keys()))
            if country:
                tag = tabs[country]['tag']
        
        # text input: create filename
        with col2:
            filename = st.text_input("Create filename", "")
            if filename:
                bool, df = search_data(filename)
                if bool:
                    st.write("⚠️ A file with this name already exists.")
                    st.session_state["SubmitError"] = True
                if filename.count("/") > 1:
                    st.write("⚠️ Only one sub-directory may be created.")
                    st.session_state["SubmitError"] = True
        
        # get filepath to save manual data
        if country and filename and not bool:
            st.session_state["SubmitError"] = False
            if filename.count("/") == 1:
                subdir = f"{MASTER_DIRECTORY}/data/{tag}/{filename[:filename.find('/')]}/"
                if not os.path.exists(subdir):
                    os.mkdir(subdir)
                filepath = subdir + filename[filename.find('/')+1:] + '.csv'
            else:
                filepath = os.getcwd() + f"/data/{tag}/{filename}.csv"
        
        # editable dataframe for manual entry
        edited = st.data_editor(st.session_state["ManualTable"],
                    use_container_width = True, num_rows = 'dynamic',
                    column_config = {"Date": st.column_config.DateColumn(),
                                     "Category": st.column_config.SelectboxColumn(options = expense_categories)}
                                     )
    
        def disable_button(edited):
            # no rows added
            bool1 = edited.shape[0] == 0
            # incomplete/unfilled cells
            bool2 = any([pd.isnull(edited.loc[ix, col]) for ix in edited.index for col in edited.columns])
            if filename and bool or bool1 or bool2:
                return True
            else:
                return False
        
        create_annotations(edited, column = "Amount", threshold = 0, labels = ["Outgoing", "Incoming"])
        
        submit_button = st.button("Submit", disabled = disable_button(edited), key = "ManualUpload")
        if submit_button and st.session_state["SubmitError"]==False:
            edited.reset_index().to_csv(filepath, index = True)
            st.write(f"Data uploaded to `~/data/{tag}/{filename}.csv`")



def calculator(master_df = pd.DataFrame()):
    st.header("⚖️ Calculator")
    st.caption("Manually add, remove or edit account values and compute total net worth in USD.")

    with st.container():
        st.caption("⏰ Estimated time: 10 minutes")
        
        def f(raw_value, currency):
            return converter[currency]*raw_value
        
        master_df["Balance in USD"] = master_df["Raw Value"]
        master_df["Balance in USD"] = master_df.apply(lambda x: f(x['Raw Value'], x['Currency']), axis = 1)
        master_df = master_df.reset_index().rename(columns = {"index": "Account"})
            
        if "CalculatorTable" not in st.session_state:
            st.session_state["CalculatorTable"] = master_df
        
        edited = st.data_editor(st.session_state["CalculatorTable"],
                                key = "edit_table",
                                num_rows = 'dynamic',
                                use_container_width = True,
                                column_config = {
                                    "Currency": st.column_config.SelectboxColumn(options = converter.keys())}
                                ) # TODO: on_change = run update_data_editor and compute running total
        
        submit_button = st.button("Export", key = "Export")
        
        if submit_button:
            master_df = update_data_editor(master_df,
                                           compulsory_cols = ['Account', 'Raw Value', 'Currency'],
                                           update_session_tag = 'edit_table')
            master_df["Balance in USD"] = master_df.apply(lambda x: f(x['Raw Value'], x['Currency']), axis = 1)
            st.session_state["CalculatorTable"] = master_df
            st.write(f"Total: ${float_to_str(sum(master_df['Balance in USD']))}")
            date_tag = datetime.today().strftime('%Y-%m-%d')
            master_df.to_csv(f"{MASTER_DIRECTORY}/data/Calculator/{date_tag}_export.csv")
            


def show_cards(country, redact):
    assert country in list(tabs.keys())
    
    try:
        if country == "Singapore":
            cc1, cc2, cc3 = st.tabs(["HSBC Revolution","OCBC 90°N","Standard Chartered Smart"])
            with cc1:
                ccards, ctext = st.columns([1, 3])
                with ccards:
                    st.image("images/hsbc-revolution.jpg", width = 175)
                if not redact:
                    with ctext:
                        st.caption("No Annual Fee | 3.25% Foreign Currency Transaction Fee")
                        st.caption("4 miles per S\$1 up to S\$1,000/month, 0.4 miles per S$1 thereafter")
                        st.caption("5:2 KrisFlyer Miles Conversion, S\$43.60 Annual Transfer Fee")
            with cc2:
                ccards, ctext = st.columns([1, 3])
                with ccards:
                    st.image("images/ocbc-90nmastercard.png", width = 175)
                if not redact:
                    with ctext:
                        st.caption("S\$196.20 Annual Fee | 3.25% Foreign Currency Transaction Fee + Mastercard Fees (~1%)")
                        st.caption("1.3 miles per S\$1 Local Spend, 2.1 miles per S\$1 Foreign Spend")
                        st.caption("1:1 KrisFlyer / Flying Blue Miles Conversion, S\$25 Conversion Fee")
                
            with cc3:
                ccards, ctext = st.columns([1, 3])
                with ccards:
                    st.image("images/sc-smart.jpg", width = 175)
                if not redact:
                    with ctext:
                        st.caption("No Annual Fee | 3.5% Foreign Currency Transaction Fee")
                        st.caption("19.2 points per S\$1 on BUS/MRT, 1.6 points per S\$1 otherwise")
                        st.caption("320 points = S\$1 | 1.015:1 KrisFlyer Miles Conversion, S\$26.75 Conversion Fee")
                    
        elif country == "United States":
            cc1, cc2 = st.tabs(["Chase United Gateway","Bank of America Travel Rewards"])
            with cc1:
                ccards, ctext = st.columns([1, 3])
                with ccards:
                    st.image("images/chase-unitedgateway.png", width = 175)
                if not redact:
                    with ctext:
                        st.caption("No Annual Fee | No Foreign Currency Transaction Fee")
                        st.caption("2 miles per \$1 on United® purchases, gas stations, local transit")
                        st.caption("1 mile per \$1 otherwise")
            with cc2:
                ccards, ctext = st.columns([1, 3])
                with ccards:
                    st.image("images/boa-travelrewards.jpg", width = 175)
                if not redact:
                    with ctext:
                        st.caption("No Annual Fee | No Foreign Currency Transaction Fee")
                        st.caption("1.5 points per \$1 on all purchases")
                        
        else:
            st.caption("_Could not display credit cards._")
            
    except Exception as e:
        print(e)

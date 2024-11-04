import streamlit as st

from src.constants import expense_categories, tabs
from src.utilities import DataDirectory

from src.frontend.upload import uploader, tabulator


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
        

import os
import sys
import pandas as pd
import altair as alt
import streamlit as st
from annotated_text import annotated_text

from decouple import config
MASTER_DIRECTORY = config('MASTER_DIRECTORY')

curr_dir = os.path.dirname(__file__)
sys.path.append(curr_dir)

from dtype_conversions import float_to_str


pd.set_option('display.precision', 2)
colors = ['#EEB64B','#FC9460','#E54264','#442261','#005B6E','#64A47F','#C3C48A']
# bcolors = ['#03DAC6', '#CF6679']


def create_annotations(df, column, threshold, labels):
    '''
    FUNCTION to sum values in a dataframe column below and exceeding a threshold and creating two annotations to express these amounts
    '''
    assert column in df.columns
    assert len(labels) == 2
    try:
        return annotated_text(
            (float_to_str(sum(df[column][df[column] < threshold])),labels[0]),
            "\t",
            (float_to_str(sum(df[column][df[column] >= threshold])), labels[1])
            )
    except Exception as e:
        print(e)
        
        
def format_table(df, column = "Amount"):
    '''
    FUNCTION to format a table by highlighting a cell in a column based on if it exceeds a value.
    input:
    - df, the input dataframe
    - column, the column to be highlighted
    - threshold, the value to be exceeded to highlight a cell
    - bcolors, the colors to be used to highlight a cell
    '''
    try:
        if column in list(df.columns):
            return df.style.applymap(highlight, subset = column)
        else:
            return df
    except Exception as e:
        print(e)


def highlight(val, threshold = 0, bcolors = ['#03DAC6', '#CF6679']):
    '''
    FUNCTION to choose which background color a cell with be highlighted with based on cell value
    '''
    assert len(bcolors) == 2, "Require two colors to be specified for highlighting."
    try:
        if val < threshold:
            color = bcolors[0]
        else:
            color = bcolors[1]
        return f'background-color: {color}'
    except Exception as e:
        print(e)
        

def horizontal_bar(chart_data, redact, size = 40):
    '''
    FUNCTION to create a horizontal stacked bar chart.
    input: chart_data, the input dataframe
    output: chart object
    '''
    try:
        chart_data.index = [""]
        data = pd.melt(chart_data.reset_index(), id_vars = ["index"])
        
        if redact:
            chart = (
                alt.Chart(data)
                .mark_bar(size = size)
                .encode(
                    x = alt.X("value",
                              type = "quantitative",
                              title = "",
                              axis = None),
                    y = alt.Y("index",
                              type = "nominal",
                              title = ""),
                    color = alt.Color("variable",
                                      type = "nominal",
                                      title = "",
                                      legend = alt.Legend(orient = 'top', columns = 3)),
                    order = alt.Order("variable",
                                      sort = "descending"),
                )
            )
            
        else:
            chart = (
                alt.Chart(data)
                .mark_bar(size = size)
                .encode(
                    x = alt.X("value",
                              type = "quantitative",
                              title = ""),
                    y = alt.Y("index",
                              type = "nominal",
                              title = ""),
                    color = alt.Color("variable",
                                      type = "nominal",
                                      title = "",
                                      legend = alt.Legend(orient = 'top', columns = 3)),
                    order = alt.Order("variable",
                                      sort = "descending"),
                )
            )
        return chart
    except Exception as e:
        print(e)


def local_css(filename):
    with open(f"{MASTER_DIRECTORY}/src/{filename}") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)


def vertical_bar(chart_data, redact):
    '''
    FUNCTION to create a vertical stacked bar chart.
    input: chart_data, the input dataframe
    output: chart object
    '''
    try:
        melt_df = pd.melt(chart_data.reset_index(), id_vars = ['Date'], value_vars = chart_data.columns)
        size = melt_df.shape[0]/5.5
        
        if redact:
            chart = (
                alt.Chart(melt_df)
                .mark_bar(size = size)
                .encode(
                    x = alt.X("Date", title = ""),
                    y = alt.Y("value", title = "", axis = None),
                    color = alt.Color("Source",
                                      scale = alt.Scale(range = colors[:len(chart_data.columns)]),
                                      legend = None),
                )
            )
        else:
            chart = (
                alt.Chart(melt_df)
                .mark_bar(size = size)
                .encode(
                    x = alt.X("Date", title = ""),
                    y = alt.Y("value", title = ""),
                    color = alt.Color("Source",
                                      scale = alt.Scale(range = colors[:len(chart_data.columns)]),
                                      legend = alt.Legend(orient = 'bottom')),
                )
            )
        return chart
    except Exception as e:
        print(e)


def update_data_editor(original_data, compulsory_cols, update_session_tag = "edit_table"):
    assert all(col in list(original_data.columns) for col in compulsory_cols)
    assert update_session_tag in st.session_state
    
    try:
        updated_df = original_data.copy()
        
        # compile all edits (add, update, delete) made to data_editor
        updates = st.session_state[update_session_tag]
        added_rows = list(updates.get("added_rows"))
        updated_rows = list(st.session_state[update_session_tag].get("edited_rows"))
        deleted_rows = st.session_state[update_session_tag].get("deleted_rows")
        
        if len(added_rows) > 0:
            # add all rows that have completed compulsory columns
            for row in added_rows:
                if all(col in row.keys() for col in compulsory_cols):
                    new_row = pd.DataFrame.from_dict(row, orient = 'index').T
                    updated_df = pd.concat([updated_df, new_row], ignore_index = True)
        
        if len(updated_rows) > 0:
            # incorporate updates to rows
            st.write(f"⚠️ WIP: Edits to be incorporated.")
            
        if len(deleted_rows) > 0:
            # output error message
            st.write(f"⚠️ ERROR: Deletions will be ignored.")
        
        return updated_df
        
    except Exception as e:
        print(e)

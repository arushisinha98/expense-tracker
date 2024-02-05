import altair as alt
import pandas as pd
import numpy as np
import streamlit as st
from decouple import config
MASTER_DIRECTORY = config('MASTER_DIRECTORY')

pd.set_option('display.precision', 2)


def format_table(df, column = "Amount"):
    '''
    FUNCTION to format a table by highlighting a column based on if it exceeds a value.
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
    FUNCTION to choose which background color a cell with be highlighted with
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
        

def horizontal_bar(chart_data, size = 40):
    '''
    FUNCTION to create a horizontal stacked bar chart.
    input: chart_data, the input dataframe
    output: chart object
    '''
    try:
        chart_data.index = [""]
        data = pd.melt(chart_data.reset_index(), id_vars = ["index"])
        
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
                                  legend = alt.Legend(orient = 'top', columns = 5)),
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

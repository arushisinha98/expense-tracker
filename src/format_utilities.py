import pandas as pd
from annotated_text import annotated_text

from dtype_conversions import float_to_str


def create_annotations(df, column, threshold, labels):
    '''
    FUNCTION to sum values in a dataframe column below and exceeding a
    threshold and creating two annotations to express these amounts.
    '''
    try:
        if column in list(df.columns):
            return annotated_text(
                (float_to_str(sum(df[column][df[column] < threshold])),
                 labels[0]),
                "\t",
                (float_to_str(sum(df[column][df[column] >= threshold])),
                 labels[1])
                )
        else:
            return ''
    except Exception as e:
        print(e)

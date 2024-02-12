import os
from datetime import date, datetime, timedelta
import pandas as pd

from decouple import config
MASTER_DIRECTORY = config('MASTER_DIRECTORY')

from constants import expense_categories, tabs
from upload_utilities import list_files


def compile_statements(country, period, exclude = ['paystubs.csv']):
    '''
    FUNCTION to compile .csv files with spending amounts and classified categories.
    input:
    - country, the subfolder to be searched and compiled
    - exclude, a list of files that are to be excluded
    '''
    assert country in list(tabs.keys())
    try:
        # compile data for specified country
        os.chdir(MASTER_DIRECTORY)
        path = os.getcwd() + f"/data/{tabs[country]['tag']}/"
        filelist = []
        for root, dirs, files in os.walk(path):
            for ff in files:
                if ff.endswith('.csv') and all(not ff.endswith(ex) for ex in exclude):
                    filelist.append(os.path.join(root,ff))
        
        # create master dataframe sorted by date with source column
        master_df = pd.DataFrame()
        for file in filelist:
            df = pd.read_csv(file)
            if "Source" not in df.columns:
                df["Source"] = file[file.find(f"{tabs[country]['tag']}/")+3:file.rfind("/")]
            master_df = master_df.append(df)
        master_df = master_df.loc[:, ~master_df.columns.str.contains('^Unnamed')]
        master_df.sort_values(by = "Date", inplace = True)
        master_df["Date"] = pd.to_datetime(master_df["Date"]).dt.date
        
        # filter based on specified period
        filtered_df = master_df.loc[(master_df["Date"] >= period[0]) &
                                    (master_df["Date"] <= period[1])]
        filtered_df = filtered_df.reset_index(drop = True)
        return filtered_df
    except Exception as e:
        print(e)


def category_table(df, period):
    '''
    FUNCTION to create expense category table.
    input: df, the input dataframe
    output: output_df, the output dateframe
    '''
    try:
        period_str = f"{datetime.strftime(period[0], '%d %b %Y')} to {datetime.strftime(period[1], '%d %b %Y')}"
        store = dict()
        for cat in expense_categories:
            if cat != "Credit Card": # remove credit card payments
                store[cat] = -1*sum(df.loc[df["Category"] == cat]["Amount"])
        output_df = pd.DataFrame.from_dict(store, orient = 'index', columns = [period_str])
        output_df = output_df.sort_index()
        return output_df.T
    except Exception as e:
        print(e)
    
    
def balance_table(df, period):
    '''
    FUNCTION to get account balance timeseries.
    input: df, the input dataframe
    output: output_df, the output dataframe
    '''
    try:
        series = df[["Date","Balance","Source"]]
        series = series[~series["Balance"].isna()] # rows with balance column filled
        series.loc[:,"Date"] = pd.to_datetime(series["Date"])
        series.set_index("Date", inplace = True)
        
        # last recorded balance of the month for each source
        output_df = pd.DataFrame()
        for source in set(series["Source"]):
            source_slice = series[series["Source"] == source].resample('M').last()
            output_df = output_df.append(source_slice)
        
        output_df.reset_index(inplace = True)
        output_df.columns = ["Date","Balance","Source"]
        return output_df
    except Exception as e:
        print(e)



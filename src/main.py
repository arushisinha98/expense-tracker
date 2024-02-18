import os
import sys
from decouple import config
MASTER_DIRECTORY = config('MASTER_DIRECTORY')

curr_dir = os.path.dirname(__file__)
sys.path.append(curr_dir)

from constants import expense_categories, tabs, converter
from app import README, MAIN


def main():
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
    
    try:
        MAIN()
        
    except Exception as e:
        README()
        print(e)


if __name__ == '__main__':
    main()

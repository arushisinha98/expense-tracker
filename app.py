import os

from src.constants import tabs

from src.main import MAIN
from src.help import HELP


def main():
    # check data directory path exists
    if not os.path.isdir('data'):
        HELP()
        raise MissingDirectoryError("Require a `data/` folder in root.")
    # check each tab has an associated currency
    if not all(['currency' in list(value.keys()) for key, value in tabs.items()]):
        HELP()
        raise MissingCurrencyError("Require each tab to have an associated currency.")
    # check each currency is accounted for in converter
    if not all(tab['currency'] in list(converter.keys()) for tab in tabs.values()):
        HELP()
        raise MissingConversionError("We do not perform real-time currency conversions. Please declare all currency conversions in `constants.py`.")
    # check data directory is organized by tab
    if not all([os.path.exists(f"data/{tab['tag']}/") for tab in tabs.values()]):
        HELP()
        raise MismatchDirectoryError("Require each tab to have an associated subdirectory in `data/`.")
    try:
        MAIN()
    except Exception as e:
        print(e)

        
if __name__ == '__main__':
    main()

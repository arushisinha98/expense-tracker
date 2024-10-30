import os
import sys

from constants import expense_categories, tabs, converter
from render import README, MAIN


def main():
    if not os.path.isdir('data'):
        raise NoDataDirectoryError
    try:
        MAIN()
    except Exception as e:
        print(e)
        README()

        
if __name__ == '__main__':
    main()

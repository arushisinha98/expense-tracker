import os
import sys

from constants import expense_categories, tabs, converter
from render import README, MAIN


def main():
    if not os.path.isdir('data'):
        README()
    try:
        MAIN()
    except Exception as e:
        print(e)

        
if __name__ == '__main__':
    main()

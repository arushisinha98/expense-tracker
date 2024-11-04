import os
import sys

from render import README, MAIN


def main():
    if not os.path.isdir('data') or not os.path.isdir('data/misc'):
        README()
    try:
        MAIN()
    except Exception as e:
        print(e)

        
if __name__ == '__main__':
    main()

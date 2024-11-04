import os

from src.main import MAIN
from src.help import HELP


def main():
    if not os.path.isdir('data') or not os.path.isdir('data/misc'):
        HELP()
    try:
        MAIN()
    except Exception as e:
        print(e)

        
if __name__ == '__main__':
    main()

"""
Script that obtains data from OSRS hiscores and displays interesting
information.

Created on Thu Apr 14 11:16:50 2022
@author: Tom Bache
"""

import argparse
import pandas as pd

# Required when running in some IDEs (e.g. Spyder)
from urllib.request import Request, urlopen


if __name__ == '__main__':

    # Parse CL arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--player', nargs=1, default='ioniph',
        help='Name of the player whose stats are to be fetched.')
    args = parser.parse_args()

    # Read players stats from OSRS hiscores
    player = str(args.player)
    req = Request('https://secure.runescape.com/m=hiscore_oldschool/hiscorepersonal?user1='+player,
                  headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    hiscores = pd.read_html(webpage)
    print(hiscores)

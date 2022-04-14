"""
Script that obtains a players data from OSRS hiscores and displays interesting
information.

Created on 14 April 2022
@author: Tom Bache
"""

import argparse
import pandas as pd

# Required when running in some IDEs (e.g. Spyder)
from urllib.request import Request, urlopen


def CleanHiscoresDataFrame(df):
    """
    Cleans dataframe read from hiscores website to make it human readable.
    Parameters
    ----------
    df : Pandas dataframe to be cleaned.

    Returns
    -------
    df : Cleaned pandas dataframe.
    """
    cols = df.iloc[1][1:]  # Extract correct column names (ignore first)
    df.drop([0, 1, 2], inplace=True)  # Drop unnecessary rows
    df.drop([0], axis=1, inplace=True)  # Drop duplicated column
    df.columns = cols
    df.set_index('Skill', inplace=True)
    df.drop('Minigame', inplace=True)  # Remove unnecessary row
    return df


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
    hiscores = pd.read_html(webpage)[2]

    # Format dataframe
    hiscores = CleanHiscoresDataFrame(hiscores)

    print(hiscores)

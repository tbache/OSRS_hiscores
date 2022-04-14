"""
Script that obtains a players data from OSRS hiscores and displays interesting
information.

Created on 14 April 2022
@author: Tom Bache
"""

import argparse
import pandas as pd
from datetime import date

# Required when running in some IDEs (e.g. Spyder)
from urllib.request import Request, urlopen


def CleanHiscoresDataFrame(df):
    """
    Cleans dataframe read from hiscores website to make it human readable.
    Sets todays date and skill name as multiindex for writing to csv later.

    Parameters
    ----------
    df : Pandas dataframe to be cleaned.

    Returns
    -------
    df : Cleaned pandas dataframe.
    """
    # Save correct column names
    cols = df.iloc[1][1:]
    # Drop unnecessary rows and columns
    df.drop([0, 1, 2], inplace=True)
    df.drop([0], axis=1, inplace=True)
    # Set column names and index
    df.columns = cols
    df.set_index('Skill', inplace=True)
    # Remove unnecessary row
    df.drop('Minigame', inplace=True)
    # Create multiindex using todays date and skill name
    index = [(date.today(), i) for i in hiscores.index]
    df.index = pd.MultiIndex.from_tuples(index, names=('Date', 'Skill'))
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

    # Clean dataframe
    hiscores = CleanHiscoresDataFrame(hiscores)

    print(hiscores)

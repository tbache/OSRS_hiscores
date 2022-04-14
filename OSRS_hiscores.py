"""
Script that obtains a players data from OSRS hiscores and displays interesting
information.

Created on 14 April 2022
@author: Tom Bache
"""
import argparse
from os.path import exists
import pandas as pd
from datetime import datetime
import numpy as np
# Required when running in some IDEs (e.g. Spyder)
from urllib.request import Request, urlopen

"""
TODO
- Read default player name from config file
- Create script that runs this script once per day
"""


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
    index = [(datetime.now(), i) for i in hiscores.index]
    df.index = pd.MultiIndex.from_tuples(index, names=('Date', 'Skill'))
    df = df.astype(np.int64)
    return df


if __name__ == '__main__':

    # Parse CL arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--player', nargs=1, default='ioniph',
        help='Name of the player whose stats are to be fetched.')
    args = parser.parse_args()

    # Set player name
    player = str(args.player)

    # Read csv file for this player and format it
    PlayerFileExists = False
    if exists(player+'-hiscores.csv'):
        PlayerFileExists = True
        hiscores_all_time = pd.read_csv(
            player+'-hiscores.csv', parse_dates=[0],
            names=['Date', 'Skill', 'Rank', 'Level', 'XP'])
        hiscores_all_time.set_index(['Date', 'Skill'], inplace=True)
        # Change datetime to date only
        hiscores_all_time.index = hiscores_all_time.index.set_levels(
            [pd.to_datetime(hiscores_all_time.index.levels[0], format='%Y-%m-%d'),
             hiscores_all_time.index.levels[1]])

    # Read players current stats from OSRS hiscores
    req = Request('https://secure.runescape.com/m=hiscore_oldschool/hiscorepersonal?user1='+player,
                  headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    hiscores = pd.read_html(webpage)[2]

    # Clean dataframe
    hiscores = CleanHiscoresDataFrame(hiscores)

    # Save current hiscores to csv file
    print("Saving current stats to CSV file:", player+'-hiscores.csv')
    hiscores.to_csv(player+'-hiscores.csv', mode='a', header=False)

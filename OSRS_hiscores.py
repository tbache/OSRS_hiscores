"""
Script that obtains a players data from OSRS hiscores and displays interesting
information.

Created on 14 April 2022
@author: Tom Bache
"""

"""
TODO
- Read default player name from config file
- Create script that runs this script once per day
"""




import argparse
from os.path import exists
import pandas as pd
from datetime import date
import numpy as np
from urllib.request import Request, urlopen  # Required when running in some IDEs (e.g. Spyder)
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
    if exists(player+'-hiscores.csv'):
        hiscores_all_time = pd.read_csv(
            player+'-hiscores.csv', parse_dates=[0],
            names=['Date', 'Skill', 'Rank', 'Level', 'XP'])
        print(hiscores_all_time)
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

    # Get unique dates present in csv file
    dates = list(set([d for (d, s) in hiscores_all_time.index]))
    print(dates)
    print(hiscores.loc[dates[0]])
    print(hiscores_all_time.loc[dates[0]])
    # Check if current stats are already present in csv file
    # Ignore rank column for now
    StatUpdateNeeded = True
    for d in dates:
        if hiscores.drop('Rank', axis=1).loc[d].equals(hiscores_all_time.drop('Rank', axis=1).loc[d]):
            print("No difference in stats since last update.")
            StatUpdateNeeded = False

    if StatUpdateNeeded:
        # Save current hiscores to CSV file
        print("Saving current stats.")
        hiscores.to_csv(player+'-hiscores.csv', mode='a', header=False)

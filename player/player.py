"""
Module containing Player class.

?????????????????????????????????????????????????

"""

import sys
import os
import pandas as pd
from datetime import datetime
import numpy as np
# Required when running in some IDEs (e.g. Spyder):
from urllib.request import Request, urlopen


class Player:
    """
    Obtains, cleans and holds the players stats.

    ...

    Attributes
    ----------
    stats : pandas dataframe

    Methods
    -------


    TODO:
        Add setters and getters
        Update docs
        Split GetPlayerStats into Get and Write
        Replace hiscores_all_time with player.stats.

    """

    def __init__(self):
        self.name = ""
        self.update = False
        self.stats = None

    def clean_player_stats(self):
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
        cols = self.stats.iloc[1][1:]
        # Drop unnecessary rows and columns
        self.stats.drop([0, 1, 2], inplace=True)
        self.stats.drop([0], axis=1, inplace=True)
        # Set column names and index
        self.stats.columns = cols
        self.stats.set_index('Skill', inplace=True)
        # Remove unnecessary row
        self.stats.drop('Minigame', inplace=True)
        # Create multiindex using todays date and skill name
        # print(self.stats.index)
        index = [(datetime.now(), i) for i in self.stats.index]
        self.stats.index = pd.MultiIndex.from_tuples(
            index, names=('Date', 'Skill'))
        self.stats = self.stats.astype(np.int64)
        # return df

    def get_player_stats_from_html(self):
        """
        Fetches player stats from hiscores website.

        Parameters
        ----------
        player : string
            Player username.
            """
        # Read players current stats from OSRS hiscores
        page_name = 'https://secure.runescape.com/m=hiscore_oldschool/hiscorepersonal?user1='+self.name
        req = Request(page_name, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        if "No player" in str(webpage):
            print("No player with name %s found. Exiting..." % (self.name))
            sys.exit()
        self.stats = pd.read_html(webpage)[2]

        # Clean dataframe
        self.clean_player_stats()

    def write_player_stats_to_csv(self):
        """
        Writes player stats to a csv file (<name>-hiscores.csv).

        """
        # Save current hiscores to csv file
        print(
            f"Saving current stats to CSV file: {self.name}-hiscores.csv")
        self.stats.to_csv(self.name+'-hiscores.csv',
                          mode='a', header=False)

    def get_player_stats_from_csv(self):
        """
        Reads player stats from a csv file (<name>-hiscores.csv).

        Checks are made to ensure the csv file exists. If it does not, the
        user is asked whether the csv file should be created.

        Returns
        -------
        self.stats : pandas dataframe
            DataFrame containing player stats.

        """
        if os.path.exists(self.name+'-hiscores.csv'):
            self.stats = pd.read_csv(
                self.name+'-hiscores.csv', parse_dates=[0],
                names=['Date', 'Skill', 'Rank', 'Level', 'XP'])
        else:
            # Must not have given --update as csv file doesn't exist
            # Ask user if they wish to update and create the csv file
            while True:
                user_input = input(
                    "CSV file for player %s does not exist. Would you like to create one? [y/n] " % (self.name))
                if user_input not in ['y', 'n', 'yes', 'no']:
                    print("Please enter one of [y/n].")
                    continue
                else:
                    break
            if user_input == "y" or user_input == "yes":
                self.get_player_stats_from_html()
                self.write_player_stats_to_csv()
                self.stats = pd.read_csv(
                    self.name+'-hiscores.csv', parse_dates=[0],
                    names=['Date', 'Skill', 'Rank', 'Level', 'XP'])
            else:
                print("Exiting...")
                sys.exit()

        return self.stats

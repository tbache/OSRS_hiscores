"""
Obtain, clean and read player's stats from OSRS hiscores.

Classes:
    Player

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
    name: player name being analysed. When set, spaces are replaced with "+".
    update: whether stats in csv file should be updated from hiscores
    stats : pandas dataframe containing player's stats
    skills : pandas dataframe containing player's skill stats (subset of stats)
    killcount : pandas dataframe containing player's boss killcount stats
                (subset of stats)
    total_killcount : pandas dataframe containing player's total boss killcount
                      (sum of 'killcount' per day)

    Methods
    -------
    clean_player_stats():
        Cleans dataframe read from hiscores website.
    get_player_stats_from_html():
        Reads dataframe from hiscores website.
    write_player_stats_to_csv():
        Writes player stats to a csv file.
    get_player_stats_from_csv():
        Reads player stats from a csv file.
    extract_skills():
        Extracts skills from self.stats.
    extract_killcount():
        Extracts boss killcount and sum of boss killcount from self.stats.

    """

    def __init__(self):
        self.__name = ""
        self.__update = False
        self.__stats = None
        self.__skills = None
        self.__killcount = None
        self.__total_killcount = None

    # Getters
    @property
    def name(self): return self.__name
    @property
    def update(self): return self.__update
    @property
    def stats(self): return self.__stats
    @property
    def skills(self): return self.__skills
    @property
    def killcount(self): return self.__killcount
    @property
    def total_killcount(self): return self.__total_killcount

    # Setters
    @name.setter
    def name(self, value):
        # Replace spaces in player name
        if " " in value:
            value = value.replace(" ", "+")
        self.__name = value

    @update.setter
    def update(self, value): self.__update = value
    @stats.setter
    def stats(self, value): self.__stats = value
    @skills.setter
    def skills(self, value): self.__skills = value
    @killcount.setter
    def killcount(self, value): self.__killcount = value
    @total_killcount.setter
    def total_killcount(self, value): self.__total_killcount = value

    # Methods
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

    def extract_skills(self):
        """
        Obtains stats for items in 'stats' considered 'skills'.
        The instance's 'skills' object is set here.

        """
        # Obtain series' corresponding to skills and concatenate them
        skill_list = ['Overall', 'Attack', 'Defence', 'Strength', 'Hitpoints',
                      'Ranged', 'Prayer', 'Magic', 'Cooking', 'Woodcutting',
                      'Fletching', 'Fishing', 'Firemaking', 'Crafting',
                      'Smithing', 'Mining', 'Herblore', 'Agility', 'Thieving',
                      'Slayer', 'Farming', 'Runecraft', 'Hunter',
                      'Construction']
        single_skills = []
        for s in skill_list:
            single_skill = self.stats[(self.stats['Skill'] == s)]
            single_skills.append(single_skill)
        self.skills = pd.concat(single_skills)

    def extract_killcount_and_total(self):
        """
        Obtains stats for items in 'stats' considered 'boss killcount'.
        All killcounts are also summed to obtain total per date.
        The instance's 'killcount' and ''total_killcount' is set by this
        method.

        """
        # Obtain killcount by removing skills from overall stats
        self.killcount = pd.merge(self.stats, self.skills, indicator=True,
                                  how='outer').query('_merge=="left_only"')
        self.killcount.drop(['_merge', 'XP'], axis=1, inplace=True)
        self.killcount.columns = ['Date', 'Boss', 'Rank', 'Kill count']

        # Create new dataframe containing date and total kill count
        unique_dates = list(self.killcount['Date'].unique())
        totals = [sum(self.killcount[self.killcount['Date'] == date]['Kill count'])
                  for date in unique_dates]
        self.total_killcount = pd.DataFrame({'Date': unique_dates,
                                             'Kill count': totals})

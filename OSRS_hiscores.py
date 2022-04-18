"""
Script that obtains a players data from OSRS hiscores and displays interesting
information.
See README for more information and usage.

Created on 14 April 2022
@author: Tom Bache
"""
import argparse
import os
import sys
import pandas as pd
from datetime import datetime
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
# Required when running in some IDEs (e.g. Spyder):
from urllib.request import Request, urlopen

plt.style.use('ggplot')


class Config:
    # TODO
    """
    Holds information read from config file

    Attributes
    ----------
    player : str
        username of player to be looked up on hiscores
    path : str
        absolute path of directory containing OSRS_hiscores.py script

    Methods
    -------
    ParseConfig():
        Reads config file and sets attributes

    """

    def __init__(self):
        self.player = ""
        self.path = ""

    def ParseConfig(self):
        conf = open("config")
        for line in conf:
            if line.startswith("player"):
                self.player = line.split("=")[1].strip()
            elif line.startswith("path"):
                self.path = line.split("=")[1].strip()


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
    # print(df.index)
    index = [(datetime.now(), i) for i in df.index]
    df.index = pd.MultiIndex.from_tuples(index, names=('Date', 'Skill'))
    df = df.astype(np.int64)
    return df


def GetPlayerStats(player):
    """
    Fetches player stats from hiscores website and writes them
    to csv file.

    Parameters
    ----------
    player : string
        Player username.
    """
    # Read players current stats from OSRS hiscores
    page_name = 'https://secure.runescape.com/m=hiscore_oldschool/hiscorepersonal?user1='+player
    req = Request(page_name, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    if "No player" in str(webpage):
        print("No player with name %s found. Exiting..." % (player))
        sys.exit()
    hiscores = pd.read_html(webpage)[2]

    # Clean dataframe
    hiscores = CleanHiscoresDataFrame(hiscores)

    # Save current hiscores to csv file
    print("Saving current stats to CSV file:", player+'-hiscores.csv')
    hiscores.to_csv(player+'-hiscores.csv', mode='a', header=False)


def RotateTickLabels(fig):
    """
    Rotates all x-axis tick labels in seaborn facetgrid

    Parameters
    ----------
    fig : seaborn facetgrid
    """
    for axes in fig.axes.flat:
        _ = axes.set_xticklabels(axes.get_xticklabels(), rotation=90)


if __name__ == '__main__':

    # Read config
    conf = Config()
    conf.ParseConfig()

    # Change current path (required for automation)
    os.chdir(conf.path)

    # Parse CL arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--player',
        help='Name of the player whose stats are to be fetched.')
    parser.add_argument(
        '--update', action='store_true', default=False,
        help='Will fetch stats from hiscores.')
    parser.add_argument(
        '--no_plot', action='store_true', default=False,
        help='If given, only update the stats and do not plot.')
    args = parser.parse_args()

    # Overwrite player name if given on CL
    if args.player:
        conf.player = str(args.player)

    # If no_plot, overwrite update
    if args.no_plot:
        print("Overwriting CL argument '--update'.")
        args.update = True

    # Update stats in csv file
    if args.update:
        GetPlayerStats(conf.player)

    # Read csv file for this player and format it
    if os.path.exists(conf.player+'-hiscores.csv'):
        hiscores_all_time = pd.read_csv(
            conf.player+'-hiscores.csv', parse_dates=[0],
            names=['Date', 'Skill', 'Rank', 'Level', 'XP'])
    else:
        # Must not have given --update as csv file doesn't exist
        # Ask user if they wish to update and create the csv file
        while True:
            user_input = input(
                "CSV file for player %s does not exist. Would you like to create one? [y/n] " % (conf.player))
            if user_input not in ['y', 'n', 'yes', 'no']:
                print("Please enter one of [y/n].")
                continue
            else:
                break
        if user_input == "y" or user_input == "yes":
            GetPlayerStats(conf.player)
            hiscores_all_time = pd.read_csv(
                conf.player+'-hiscores.csv', parse_dates=[0],
                names=['Date', 'Skill', 'Rank', 'Level', 'XP'])
        else:
            print("Exiting...")
            sys.exit()

    # Exit script after writing to csv file if user wishes
    if args.no_plot:
        print("Exiting without plotting.")
        sys.exit()

    # Create dataframe containing only "skills"
    skill_list = ['Overall', 'Attack', 'Defence', 'Strength', 'Hitpoints',
                  'Ranged', 'Prayer', 'Magic', 'Cooking', 'Woodcutting',
                  'Fletching', 'Fishing', 'Firemaking', 'Crafting', 'Smithing',
                  'Mining', 'Herblore', 'Agility', 'Thieving', 'Slayer',
                  'Farming', 'Runecraft', 'Hunter', 'Construction']
    single_skills = []
    for s in skill_list:
        single_skill = hiscores_all_time[(hiscores_all_time['Skill'] == s)]
        single_skills.append(single_skill)
    skills = pd.concat(single_skills)

    # Create dataframe containing only "kill count" by removing skill rows
    killcount = pd.merge(hiscores_all_time, skills, indicator=True,
                         how='outer').query('_merge=="left_only"')
    killcount.drop(['_merge', 'XP'], axis=1, inplace=True)
    killcount.columns = ['Date', 'Boss', 'Rank', 'Kill count']

    # print(skills)
    # print(killcount)

    # Plot skills
    skills_plot = sns.FacetGrid(data=skills, col='Skill', col_wrap=4,
                                sharey=False, height=3.5, aspect=1.5)
    skills_plot.map(sns.lineplot, 'Date', 'XP')
    for ax, (_, subdata) in zip(skills_plot.axes, skills.groupby('Skill', sort=False)):
        ax2 = ax.twinx()
        subdata.plot(x='Date', y='Level', ax=ax2, legend=False, color='b')
        ax.set_ylabel('XP')
        ax2.set_ylabel('Level')
    RotateTickLabels(skills_plot)
    skills_plot.add_legend()
    plt.tight_layout()

    # Plot killcount
    killcount_plot = sns.FacetGrid(data=killcount, col='Boss', col_wrap=6,
                                   sharey=False)
    killcount_plot.map(sns.lineplot, 'Date', 'Kill count')
    RotateTickLabels(killcount_plot)
    plt.tight_layout()

    plt.show()

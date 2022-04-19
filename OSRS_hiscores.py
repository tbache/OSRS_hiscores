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
from plotly.subplots import make_subplots
from plotly.offline import plot
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches
# Required when running in some IDEs (e.g. Spyder):
from urllib.request import Request, urlopen

plt.style.use('ggplot')


class Config:
    """
    Holds information read from config file

    Attributes
    ----------
    player : str
        username of player to be looked up on hiscores
    update: bool
        update players csv file from hiscores.
    no_plot: bool
        force update the players stats but do not plot them.

    Methods
    -------
    ParseConfig():
        Reads config file and sets attributes
    Print():
        Prints the config options given to the script.

    """

    def __init__(self):
        self.__player = ""
        self.__update = False
        self.__no_plot = False

    @property
    def player(self): return self.__player
    @property
    def update(self): return self.__update
    @property
    def no_plot(self): return self.__no_plot
    @player.setter
    def player(self, val): self.__player = val
    @update.setter
    def update(self, val): self.__update = val
    @no_plot.setter
    def no_plot(self, val): self.__no_plot = val

    def ParseConfig(self):
        conf = open("config")
        for line in conf:
            if line.startswith("#"):
                continue
            val = line.split("=")[1].strip()
            if line.startswith("player"):
                self.player = val
            elif line.startswith("update"):
                if val.lower() == "true":
                    self.update = True
            elif line.startswith("no_plot"):
                if val.lower() == "true":
                    self.no_plot = True

    def Print(self):
        print("Options provided:")
        print("\tplayer:", self.player)
        print("\tupdate:", str(self.update))
        print("\tno_plot:", str(self.no_plot))


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

    # Overwrite config file option if given on command line
    if args.player:
        conf.player = str(args.player)
    if args.update:
        conf.update = True
    if args.no_plot or conf.no_plot:
        conf.no_plot = True
        # If no_plot=True, also overwrite update
        args.update = True
        conf.update = True

    # Check for spaces in player name
    if " " in conf.player:
        conf.player = conf.player.replace(" ", "+")

    # Print config options
    conf.Print()

    # Update stats in csv file
    if conf.update:
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
    if conf.no_plot:
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

    # Create dataframe containing date and total kill count
    unique_dates = list(killcount['Date'].unique())
    total_killcount = [sum(killcount[killcount['Date'] == date]['Kill count'])
                       for date in unique_dates]
    total_killcount = pd.DataFrame({'Date': unique_dates,
                                    'Kill count': total_killcount})

    # print(skills)
    # print(killcount)

    # Create interactive plots of overall level/XP and total boss kill count
    # Note that this plot will open in the default browser
    overall_plot = make_subplots(rows=2, cols=2,
                                 vertical_spacing=0.2,
                                 specs=[[{}, {}],
                                        [{"colspan": 2}, None]])
    overall_plot.append_trace(go.Scatter(x=skills[(skills['Skill'] ==
                                                   'Overall')]['Date'],
                                         y=skills[(skills['Skill'] ==
                                                   'Overall')]['Level'],
                                         name='Level', mode='lines'),
                              row=1, col=1)
    overall_plot.append_trace(go.Scatter(x=skills[(skills['Skill'] ==
                                                   'Overall')]['Date'],
                                         y=skills[(skills['Skill'] ==
                                                   'Overall')]['XP'],
                                         name='XP', mode='lines'),
                              row=1, col=2)
    overall_plot.append_trace(go.Scatter(x=total_killcount['Date'],
                                         y=total_killcount['Kill count'],
                                         name='Kill count', mode='lines'),
                              row=2, col=1)
    overall_plot.update_xaxes(title_text='Date', row=1, col=1)
    overall_plot.update_xaxes(title_text='Date', row=1, col=2)
    overall_plot.update_xaxes(title_text='Date', row=2, col=1)
    overall_plot.update_yaxes(title_text='Total level', row=1, col=1)
    overall_plot.update_yaxes(title_text='Total XP', row=1, col=2)
    overall_plot.update_yaxes(title_text='Total boss kill count', row=2, col=1)
    overall_plot.update_layout(title_text='Overall stats')
    plot(overall_plot, auto_open=True, filename='overall_stats.html')

    # Plot skills on facetgrid (one skill per plot)
    skills_plot = sns.FacetGrid(data=skills, col='Skill', col_wrap=4,
                                sharey=False, height=3.5, aspect=1.5)
    skills_plot.map(sns.lineplot, 'Date', 'XP')
    # Add plot of level to XP plot using a 2nd y-axis
    for ax, (_, subdata) in zip(skills_plot.axes, skills.groupby('Skill', sort=False)):
        ax2 = ax.twinx()
        subdata.plot(x='Date', y='Level', ax=ax2, legend=False, color='b')
        ax.set_ylabel('XP')
        ax2.set_ylabel('Level')

        # Create legend (colours obtained via plt.gca().lines[-1].get_color())
        name_to_color = {
            'XP': (0.8862745098039215, 0.2901960784313726, 0.2),
            'Level': 'b'
        }
        patches = [matplotlib.patches.Patch(
            color=v, label=k) for k, v in name_to_color.items()]
        plt.legend(handles=patches, loc='upper left')
    RotateTickLabels(skills_plot)
    plt.tight_layout()

    # Plot killcount on facetgrid (one boss per plot)
    killcount_plot = sns.FacetGrid(data=killcount, col='Boss', col_wrap=6,
                                   sharey=False)
    killcount_plot.map(sns.lineplot, 'Date', 'Kill count')
    RotateTickLabels(killcount_plot)
    plt.tight_layout()

    plt.show()

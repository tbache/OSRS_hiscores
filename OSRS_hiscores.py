"""
Script that obtains a players data from OSRS hiscores and displays interesting
information.
See README for more information and usage.

Created on 14 April 2022
@author: Tom Bache
"""
import configparser
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


def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


def print_config(conf):
    for sec in conf.sections():
        print(sec+":")
        for tup in conf.items(sec):
            print(f"\t {tup[0]}: {tup[1]}")


if __name__ == '__main__':

    # Read config file
    config = read_config()

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
        config['PlayerSettings']['player'] = str(args.player)
    if args.update:
        config['PlayerSettings']['update'] = 'True'
    if args.no_plot or config['PlayerSettings'].getboolean('no_plot'):
        config['PlotSettings']['no_plot'] = 'True'
        # If no_plot=True, also overwrite update
        args.update = True
        config['PlayerSettings']['update'] = 'True'

    # Print config options
    print_config(config)

    # Set config values
    player = config['PlayerSettings']['player']
    update = config['PlayerSettings'].getboolean('update')
    no_plot = config['PlotSettings'].getboolean('no_plot')

    # Check for spaces in player name
    if " " in player:
        player = player.replace(" ", "+")

    # Update stats in csv file
    if update:
        GetPlayerStats(player)

    # Read csv file for this player and format it
    if os.path.exists(player+'-hiscores.csv'):
        hiscores_all_time = pd.read_csv(
            player+'-hiscores.csv', parse_dates=[0],
            names=['Date', 'Skill', 'Rank', 'Level', 'XP'])
    else:
        # Must not have given --update as csv file doesn't exist
        # Ask user if they wish to update and create the csv file
        while True:
            user_input = input(
                "CSV file for player %s does not exist. Would you like to create one? [y/n] " % (player))
            if user_input not in ['y', 'n', 'yes', 'no']:
                print("Please enter one of [y/n].")
                continue
            else:
                break
        if user_input == "y" or user_input == "yes":
            GetPlayerStats(player)
            hiscores_all_time = pd.read_csv(
                player+'-hiscores.csv', parse_dates=[0],
                names=['Date', 'Skill', 'Rank', 'Level', 'XP'])
        else:
            print("Exiting...")
            sys.exit()

    # Exit script after writing to csv file if user wishes
    if no_plot:
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

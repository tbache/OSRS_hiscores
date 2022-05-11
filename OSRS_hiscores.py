"""
Script that obtains a players data from OSRS hiscores and displays interesting
information.
See README for more information and usage.

Created on 14 April 2022
@author: Tom Bache
"""

import argparse
import sys
import matplotlib.pyplot as plt

# Own packages
from config.config import read_config, print_config
from player.player import Player
import plotting

# Plotting options
plt.style.use('ggplot')


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

    # Create Player instance
    player = Player()

    # Set config values
    player.name = config['PlayerSettings']['player']
    player.update = config['PlayerSettings'].getboolean('update')
    no_plot = config['PlotSettings'].getboolean('no_plot')

    # Check for spaces in player name
    if " " in player.name:
        player.name = player.name.replace(" ", "+")

    # Update stats in csv file
    if player.update:
        player.get_player_stats_from_html()
        player.write_player_stats_to_csv()

    # Read csv file for this player
    player.get_player_stats_from_csv()

    # Exit script after writing to csv file if user wishes
    if no_plot:
        print("Exiting without plotting.")
        sys.exit()

    # Split overall stats into "skills" and "killcount"
    player.extract_skills()
    player.extract_killcount_and_total()

    # Create interactive plots of overall level/XP and total boss kill count
    # Note that this plot will open in the default browser
    plotting.summary.create_summary_plots(player)

    # Plot skills on facetgrid (one skill per plot)
    plotting.grid_plots.plot_skills(player)

    # Plot killcount on facetgrid (one boss per plot)
    plotting.grid_plots.plot_killcount(player)

    plt.show()

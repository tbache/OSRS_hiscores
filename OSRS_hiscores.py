"""
Script that obtains a players data from OSRS hiscores and displays interesting
information.
See README for more information and usage.

Created on 14 April 2022
@author: Tom Bache
"""

import sys
import matplotlib.pyplot as plt

# Own packages
from config.config import read_config, parse_cl, print_config
from player.player import Player
import plotting

# Plotting options
plt.style.use('ggplot')


if __name__ == '__main__':

    # Read config file
    config = read_config()

    # Parse command line arguments and overwrite config file option if option
    # given on command line
    config = parse_cl(config)

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

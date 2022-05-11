"""
Functions for reading and printing the config file used by OSRS_hiscores.py.

Functions:
    read_config()
    parse_cl(ConfigParser)
    print_config(ConfigParser)

"""

import os.path
import sys
import configparser
import argparse

from config.generate_config import generate_config


def read_config():
    """
    Reads config.ini file. If it doesn't already exist, it is created.

    Returns
    -------
    config : ConfigParser
        Object containing settings present in config file.

    """
    # If config file doesn't exist, generate it
    if not os.path.exists('config.ini'):
        print('Config file does not exist.')
        print('Generating file using default parameters.')
        generate_config()
        print('Config file generated - please edit and re-run. Exiting...')
        sys.exit()

    # Config file exists, read it
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


def parse_cl(conf):
    """
    Parses the command line arguments and overwrites options set in config
    file if any CL args are given.

    Parameters
    ----------
    conf : ConfigParser
        Object containing settings present in config file.

    Returns
    -------
    conf : ConfigParser
        Object containing settings present in config file, overwritten with
        CL args if they are given.

    """
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
        conf['PlayerSettings']['player'] = str(args.player)
    if args.update:
        conf['PlayerSettings']['update'] = 'True'
    if args.no_plot or conf['PlayerSettings'].getboolean('no_plot'):
        conf['PlotSettings']['no_plot'] = 'True'
        # If no_plot=True, also overwrite update
        args.update = True
        conf['PlayerSettings']['update'] = 'True'

    return conf


def print_config(conf):
    """
    Prints config options, separated into sections.

    Parameters
    ----------
    conf : ConfigParser
        Object read by read_config().

    """
    for sec in conf.sections():
        print(sec+":")
        for tup in conf.items(sec):
            print(f"\t {tup[0]}: {tup[1]}")

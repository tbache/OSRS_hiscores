"""
Functions for reading and printing the config file used by OSRS_hiscores.py.
"""

import os.path
import sys
import configparser

from config.generate_config import GenerateConfig


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
        GenerateConfig()
        print('Config file generated - please edit and re-run. Exiting...')
        sys.exit()

    # Config file exists, read it
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


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

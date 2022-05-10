"""
Script to generate the config file required by OSRS_hiscores.py.
"""

import configparser


def generate_config():
    """
    Generates config file using default settings. This file is read by
    OSRS_hiscores.py when obtaining hiscores data.

    """
    # Create config handler
    config_file = configparser.ConfigParser()

    # Add player settings section
    config_file.add_section("PlayerSettings")
    config_file.set("PlayerSettings", "player", "Zezima")
    config_file.set("PlayerSettings", "update", "False")

    # Add plot settings section
    config_file.add_section("PlotSettings")
    config_file.set("PlotSettings", "no_plot", "False")

    # Write default settings to new config file
    with open(r"config.ini", 'w') as configfileObj:
        config_file.write(configfileObj)
        print("Config file 'config.ini' created.")

    # Read and print default settings from config file
    with open("config.ini", "r") as configfileObj:
        content = configfileObj.read()
        print("Contents of the config file:\n")
        print(content)


if __name__ == '__main__':
    generate_config()

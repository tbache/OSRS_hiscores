"""

"""

import configparser

config_file = configparser.ConfigParser()

config_file.add_section("PlayerSettings")
config_file.set("PlayerSettings", "player", "Zezima")
config_file.set("PlayerSettings", "update", "False")

config_file.add_section("PlotSettings")
config_file.set("PlotSettings", "no_plot", "False")

with open(r"config.ini", 'w') as configfileObj:
    config_file.write(configfileObj)
    # configfileObj.close()

print("Config file 'config.ini' created.")

with open("config.ini", "r") as configfileObj:
    # read_file = open("config.ini", "r")
    content = configfileObj.read()
    print("Contents of the config file:\n")
    print(content)
    # read_file.close()

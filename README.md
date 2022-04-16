OSRS_hiscores.
Reads data from the OSRS hiscores for a certain player, saves
their stats and plots the change in stats over time to show the
accounts progress.
Hiscores available at:
https://secure.runescape.com/m=hiscore_oldschool/overall
The data is saved in a local CSV file. The CSV file is called
<player>-hiscores.csv where <player> is the players username.

Author: Tom Bache (https://github.com/tbache)


Installation
Clone from https://github.com/tbache/OSRS_hiscores

Package requirements
Python3, argparse, os, pandas, datetime, numpy, seaborn, matplotlib,
urllib

Running
The below should be prefixed with whatever system command you
require to run python scripts on your system.

OSRS_hiscores.py [-h] [--player PLAYER] [--update]

Optional arguments:
-h, --help:         Show help message.
--player PLAYER     Name of the player whose stats are to displayed.
--update            Update players stats from the hiscores.

Example:
python OSRS_hiscores.py --player Zezima --update


TODO:
- Add proper markdown.
- If new player, ask user whether stats should be fetched even if update isn't included.'
- Test on linux

Future potential features
- Read default player name from config file so that my username isn't published
- Create script that runs this script once per day

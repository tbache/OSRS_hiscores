### OSRS_hiscores
Reads data from the OSRS hiscores for a certain player, saves their stats and
plots the change in stats over time to show the accounts progress.

The data is saved in a local CSV file. The CSV file is called
<player>-hiscores.csv where <player> is the players username.
Three plots are produced. See examples section below for more details.

The OSRS hiscores are available at:
https://secure.runescape.com/m=hiscore_oldschool/overall

Author: Tom Bache (https://github.com/tbache)

---

### Installation
Clone from https://github.com/tbache/OSRS_hiscores

System/package requirements:
Python3, argparse, os, pandas, datetime, numpy, seaborn, matplotlib,
urllib, plotly

---

### Running
Currently only tested on Windows 10. Plan to test on Linux in the future.
Unfortunately I have no access to a Mac so no support is planned.

The below should be prefixed with whatever system command you require to run
python scripts on your system.
The command line options can also be set in the config file "config" if that
is preferable.

OSRS_hiscores.py [-h] [--player PLAYER] [--update] [--no-plot]

Optional arguments:
-h, --help:         Show help message.
--player PLAYER     Name of the player whose stats are to displayed.
--update            Update players stats from the hiscores.
--no-plot           Force update the players stats but do not plot them.

Example:
run OSRS_hiscores.py --player Zezima --update

Automatic running
The stats for a certain character can be automatically updated. See
"automation_instructions.txt" for details.

---

### Example
Example data and plots are in the `example_plots/` directory. See the README
there for more details.

---

### Future features
- Setup script that automatically sets up the automation.bat file without user input.
- Test on Linux

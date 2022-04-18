:: Template batch file for automatically running the OSRS_hiscores.py script
:: on Windows. See "automation_instructions.txt" for instructions.
set path="C:\user\OSRS_hiscores"
cd %path%
set opt=--no_plot
"C:\Python39\python.exe" "C:\user\OSRS_hiscores\OSRS_hiscores.py" %opt%
pause

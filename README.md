# Datheon Python Programming Internship

These are my submissions for the Datheon Python internship. I did two of the four tasks: a Hangman game and a portfolio tracker. Both run with plain Python 3, nothing extra needed to install.

```
Datheon_Python_Programming_Internship/
├── TASK_1_HANGMAN/
│   ├── Hangman_Game.py
│   └── words.txt
├── TASK_2_PORTFOLIO/
│   ├── portfolio.py
│   ├── sample_prices.csv
│   ├── constituents.csv
│   └── portfolio_summary.csv
├── TASK_3_ORGANIZER/
│   ├── TAST_FOLDER
│   ├── organizer.log
│   └── Organizer.py
└── README.md
```

## Task 1: Hangman

A simple Hangman game you play in the terminal. The gallows is drawn in ASCII and gets filled in with every wrong guess.

The words come from `words.txt`, which is the Google 10,000 common English words list. The script ignores anything shorter than 5 letters or with non-letter characters, so you end up with about 7,700 words to guess from. You get 6 wrong guesses. If you type something that isn't a single letter, or repeat a guess, it just asks again and doesn't count it against you.

Run it:

```
cd TASK_1_HANGMAN
python Hangman_Game.py
```

## Task 2: Portfolio Tracker

You enter a ticker, the price you bought at, and how many shares. When you're done (press Enter on an empty ticker) it prints a table with what you invested, what it's worth now, and the gain or loss in money and percent. It also adds the results to `portfolio_summary.csv`, with a timestamp, so every run is kept.

A few things I added along the way:
- If you enter the same ticker twice, it combines them and works out the average buy price.
- Tickers are checked against `constituents.csv` (the S&P 500 list), so typos get rejected. That file also gives the company name for the CSV.
- A ticker with no price available is skipped with a message instead of crashing the program.

About prices: the S&P 500 file doesn't have any, so I made `sample_prices.csv`. Only a few of the well-known stocks have realistic numbers. The rest are made-up placeholders, so don't treat them as real market data. If you want real prices, install yfinance and run it with `--live`. It falls back to the sample file if that fails.

```
cd TASK_2_PORTFOLIO
python portfolio.py
python portfolio.py --live
```

Sample output:

```
Ticker     Shares        Buy    Current     Invested        Value   Gain/Loss        %
AAPL           10     200.00     225.50     2,000.00     2,255.00     +255.00  +12.75%
MSFT            5     450.00     425.30     2,250.00     2,126.50     -123.50   -5.49%
MMM            15     300.00     487.50     4,500.00     7,312.50   +2,812.50  +62.50%   
--------------------------------------------------------------------------------------
TOTAL                                       8,750.00    11,694.00   +2,944.00  +33.65% 
======================================================================================
```

## TASK 3: ORGANIZER
# Task 3: File Organizer
 
A Python script that cleans up a messy folder (like Downloads) by moving every file into a category folder based on its extension.
 
## What it does
 
- Looks at each file's extension and moves it into one of these folders: `Documents`, `Images`, `Videos`, `Audio`, `Archives` or `Code`.
- Creates the category folders by itself, only when a file needs one.
- Prints every move on screen and saves the same log to `organizer.log` with a timestamp.
- Ends with a summary: files moved per category, renamed, skipped and errors.
## How I handled the tricky parts
 
- **Same file name already there:** the new file gets `_1`, `_2` and so on (`report.pdf` becomes `report_1.pdf`). Nothing is overwritten.
- **Permission errors:** a locked or protected file is logged as an error and the script carries on with the rest instead of crashing.
- **Files it shouldn't touch:** hidden files, unfinished downloads (`.crdownload`, `.part`) and unknown file types stay where they are. With `--others` the unknown ones go to an `Others` folder.
- **Running twice:** files already in the right folder are left alone, so a second run does nothing.
## How to run
 
```
python organizer.py --dry-run                         # preview only, nothing moves
python organizer.py                                   # organize your Downloads folder
python organizer.py "C:/path/to/folder"               # organize any folder
python organizer.py "C:/path/to/folder" --recursive   # include subfolders
python organizer.py "C:/path/to/folder" --others      # unknown types go to /Others
```
 
I'd recommend `--dry-run` first on a new folder.
 
## How I tested it
 
1. I made a folder called `TEST_FOLDER` and dropped a mix of messy files into it: some `.jpg` / `.jpeg` images, some `.mp3` sound clips and some `.mp4` videos, all sitting together in one place.
2. I ran the script with the path of that folder.
3. It created `Images`, `Audio` and `Videos` folders and moved each file into the right one.
The test folder had 9 files in total (4 images, 2 sound clips and 3 videos). This is the log the script wrote:
 
```
INFO | Organizing: ...\TEST_FOLDER
INFO | MOVED  capcut-explosion-sound.mp3  ->  Audio/capcut-explosion-sound.mp3
INFO | MOVED  gunshot-sound.mp3  ->  Audio/gunshot-sound.mp3
INFO | MOVED  images.jpg  ->  Images/images.jpg
INFO | MOVED  istockphoto-157373207-612x612.jpg  ->  Images/istockphoto-157373207-612x612.jpg
INFO | MOVED  vlipsy-dog-with-bone-complete-shock-uUUcbXJ6.mp4  ->  Videos/vlipsy-dog-with-bone-complete-shock-uUUcbXJ6.mp4
...
 
============================================
             EXECUTION SUMMARY
============================================
  Audio            2
  Images           4
  Videos           3
--------------------------------------------
  Files moved                9
  Renamed (name clash)       0
  Skipped                    0
  Errors                     0
============================================
```
 
(Some lines are left out here to keep it short.)
 
All 9 files went to the right folders with no errors.

## Requirements

- Python 3.8 or newer
- Built-in modules only (`random`, `os`, `csv`, `sys`, `datetime`, `shutil`, `pathlib`, `logging`, `argparse`), so nothing to install
- Optional: `yfinance`, only for Task 2 with `--live` (`pip install yfinance`)
- Task 1 needs `words.txt` and Task 2 needs `sample_prices.csv` in the same folder as the script
- Task 3 needs read and write permission on the folder being organized

— ```DINESH DAYAL```

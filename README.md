# Datheon Python Programming Internship

These are my submissions for the Datheon Python internship. I did two of the four tasks: a Hangman game and a portfolio tracker. Both run with plain Python 3, nothing extra needed to install.

```
Datheon_Python_Programming_Internship/
├── README.md
├── TASK_1_HANGMAN/
│   ├── Hangman_Game.py
│   └── words.txt
└── TASK_2_PORTFOLIO/
    ├── portfolio.py
    ├── sample_prices.csv
    ├── constituents.csv
    └── portfolio_summary.csv
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

## Requirements

Python 3.8+. `yfinance` is only needed for `--live` (`pip install yfinance`).

— DINESH DAYAL

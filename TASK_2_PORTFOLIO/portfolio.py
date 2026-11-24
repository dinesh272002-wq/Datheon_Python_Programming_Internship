"""Investment Portfolio Tracker.

Enter ticker symbols, buy prices and share quantities. The script computes the
invested capital, current market value and gain/loss % per holding, prints a
formatted table, and appends a summary to portfolio_summary.csv.

Price sources (in order):
  1. Live prices via yfinance (only if you pass --live and yfinance is installed)
  2. sample_prices.csv (Symbol,Price) next to this script

Optional: if constituents.csv (S&P 500 dataset) is next to this script, tickers
are validated against it and company names are shown.
"""

import csv
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRICES_FILE = os.path.join(BASE_DIR, "sample_prices.csv")
CONSTITUENTS_FILE = os.path.join(BASE_DIR, "constituents.csv")
SUMMARY_FILE = os.path.join(BASE_DIR, "portfolio_summary.csv")

SUMMARY_HEADER = [
    "Timestamp", "Ticker", "Company", "Shares", "Buy Price",
    "Current Price", "Invested", "Market Value", "Gain/Loss", "Gain/Loss %",
]


# ---------- Data loading ----------

def load_prices(path=PRICES_FILE):
    """Return {ticker: price} from a Symbol,Price CSV."""
    prices = {}
    try:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    prices[row["Symbol"].strip().upper()] = float(row["Price"])
                except (KeyError, ValueError):
                    continue
    except FileNotFoundError:
        print(f"Warning: {os.path.basename(path)} not found.")
    return prices


def load_companies(path=CONSTITUENTS_FILE):
    """Return {ticker: company name} from the S&P 500 dataset, if present."""
    companies = {}
    try:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                companies[row["Symbol"].strip().upper()] = row.get("Security", "")
    except FileNotFoundError:
        pass
    return companies


def get_live_price(ticker):
    """Fetch the latest price with yfinance; return None on any failure."""
    try:
        import yfinance as yf
        price = yf.Ticker(ticker).fast_info["last_price"]
        return float(price) if price else None
    except Exception:
        return None


def get_price(ticker, sample_prices, live=False):
    if live:
        price = get_live_price(ticker)
        if price is not None:
            return price
    return sample_prices.get(ticker)


# ---------- Input ----------

def ask_float(prompt, minimum_exclusive=0.0):
    while True:
        raw = input(prompt).strip().replace(",", "")
        try:
            value = float(raw)
            if value > minimum_exclusive:
                return value
        except ValueError:
            pass
        print("  [!] Please enter a number greater than 0.")


def collect_positions(companies, known_prices):
    """Interactively build {ticker: {"shares": x, "buy_price": y}}."""
    portfolio = {}
    print("Enter your holdings. Press Enter on an empty ticker to finish.\n")
    while True:
        ticker = input("Ticker symbol: ").strip().upper()
        if not ticker:
            if portfolio:
                break
            print("  [!] Add at least one holding.")
            continue
        if not ticker.replace(".", "").replace("-", "").isalpha():
            print("  [!] Invalid ticker. Use letters only (e.g. AAPL).")
            continue
        if companies and ticker not in companies:
            print(f"  [!] {ticker} is not in the S&P 500 list.")
            continue
        if not companies and ticker not in known_prices:
            print(f"  [i] No sample price for {ticker}; will be skipped unless --live works.")

        buy_price = ask_float("  Buy price per share: ")
        shares = ask_float("  Number of shares: ")

        if ticker in portfolio:  # merge repeat buys using weighted average cost
            old = portfolio[ticker]
            total_shares = old["shares"] + shares
            avg = (old["shares"] * old["buy_price"] + shares * buy_price) / total_shares
            portfolio[ticker] = {"shares": total_shares, "buy_price": avg}
        else:
            portfolio[ticker] = {"shares": shares, "buy_price": buy_price}
        print(f"  Added {shares:g} x {ticker} @ {buy_price:,.2f}\n")
    return portfolio


# ---------- Calculations ----------

def analyse(portfolio, sample_prices, companies, live=False):
    rows, skipped = [], []
    for ticker, pos in portfolio.items():
        current = get_price(ticker, sample_prices, live)
        if current is None:
            skipped.append(ticker)
            continue
        invested = pos["shares"] * pos["buy_price"]
        value = pos["shares"] * current
        gain = value - invested
        rows.append({
            "ticker": ticker,
            "company": companies.get(ticker, ""),
            "shares": pos["shares"],
            "buy": pos["buy_price"],
            "current": current,
            "invested": invested,
            "value": value,
            "gain": gain,
            "pct": gain / invested * 100,
        })
    return rows, skipped


# ---------- Output ----------

def print_report(rows):
    line = "=" * 86
    print("\n" + line)
    print(f"{'PORTFOLIO SUMMARY':^86}")
    print(line)
    print(f"{'Ticker':<8}{'Shares':>9}{'Buy':>11}{'Current':>11}"
          f"{'Invested':>13}{'Value':>13}{'Gain/Loss':>12}{'%':>9}")
    print("-" * 86)
    for r in rows:
        print(f"{r['ticker']:<8}{r['shares']:>9g}{r['buy']:>11,.2f}{r['current']:>11,.2f}"
              f"{r['invested']:>13,.2f}{r['value']:>13,.2f}{r['gain']:>+12,.2f}{r['pct']:>+8.2f}%")
    print("-" * 86)

    invested = sum(r["invested"] for r in rows)
    value = sum(r["value"] for r in rows)
    gain = value - invested
    pct = gain / invested * 100 if invested else 0.0
    print(f"{'TOTAL':<8}{'':>9}{'':>11}{'':>11}"
          f"{invested:>13,.2f}{value:>13,.2f}{gain:>+12,.2f}{pct:>+8.2f}%")
    print(line)
    print(f"Total invested capital : {invested:>14,.2f}")
    print(f"Current market value   : {value:>14,.2f}")
    print(f"Overall {'gain' if gain >= 0 else 'loss'}           : {gain:>+14,.2f} ({pct:+.2f}%)")
    return invested, value, gain, pct


def write_summary(rows, totals, path=SUMMARY_FILE):
    """Append this run to the CSV (header is written only for a new file)."""
    invested, value, gain, pct = totals
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_file = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(SUMMARY_HEADER)
        for r in rows:
            writer.writerow([stamp, r["ticker"], r["company"], f"{r['shares']:g}",
                             f"{r['buy']:.2f}", f"{r['current']:.2f}",
                             f"{r['invested']:.2f}", f"{r['value']:.2f}",
                             f"{r['gain']:.2f}", f"{r['pct']:.2f}"])
        writer.writerow([stamp, "TOTAL", "", "", "", "",
                         f"{invested:.2f}", f"{value:.2f}", f"{gain:.2f}", f"{pct:.2f}"])
    print(f"\nSummary saved to {os.path.basename(path)}")


def main():
    live = "--live" in sys.argv
    print("=" * 40)
    print("      INVESTMENT PORTFOLIO TRACKER")
    print("=" * 40)

    sample_prices = load_prices()
    companies = load_companies()
    portfolio = collect_positions(companies, sample_prices)

    rows, skipped = analyse(portfolio, sample_prices, companies, live)
    if skipped:
        print(f"\n[!] No price available for: {', '.join(skipped)} (skipped)")
    if not rows:
        print("Nothing to report.")
        return

    totals = print_report(rows)
    write_summary(rows, totals)


if __name__ == "__main__":
    main()
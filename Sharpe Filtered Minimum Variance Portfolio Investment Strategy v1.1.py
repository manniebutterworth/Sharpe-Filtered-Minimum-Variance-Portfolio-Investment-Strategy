
print(f"\n--------------------------------------------------------------------------------------------")
print("------------- SHARPE FILTERED MINIMUM VARIANCE PORTFOLIO INVESTMENT STRATEGY v1.1 -------------")
print("-----------------------------------------------------------------------------------------------")

# ---------- IMPORT LIBRARIES ----------

print(f"\nImporting libraries...")

import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# ---------- CONTROLS ----------

download_data = False   # True when downloading price data from yfinance | False when loading from existing CSV.

raw_price_data_interval = "1d"
raw_price_data_period = "6mo"
raw_price_data_file_path = f"/Users/emmanuelbutterworth/Desktop/Price Data/US Equity Raw Prices ({raw_price_data_period} at {raw_price_data_interval}).csv"

initial_capital = 10_000
rf = 0.0433 # Annual Compounding
portfolio_assets_considered = 30

current_capital = 10_000 # Future versions to have API connection for live portfolio value
cppi_floor = initial_capital * 0.9
cppi_multiplier = 5

benchmarks = [
            "S&P 500 Index",
            "Nasdaq-100",
            "Dow Jones Industrial Average",
            "Russell 2000",
            "Vanguard Total Market Index",
        ]

# ---------- GENERAL FUNCTIONS ----------

def printx(title: str, x, as_percentage: bool = False):
    """
    Cleanly print a titled value or tabular object, optionally formatted as percentages.

    If `x` is a number, prints the value. Otherwise prints `x.shape` and the first 5 rows.
    When `as_percentage=True`, values are multiplied by 100 and displayed with a '%' suffix.

    Args:
        title: Label printed above the output.
        x: A scalar (int/float) or a table-like object with `.shape` and `.head()`.
        as_percentage: If True, format numeric output as percentages.
    """
    if isinstance(x, (float, int)):

        print(f"\n {title}:")

        if as_percentage == True:
            print(f"\n{(x * 100).round(2).astype(str) + "%"}")
        else:
            print(f"\n{x.round(4)}")

    else:

        print(f"\n {title} {x.shape}:")

        if as_percentage == True:
            print(f"\n{(x.head() * 100).round(2).astype(str) + "%"}")
        else:
            print(f"\n{x.head().round(4)}")
 
def print_sorted(title: str, x, as_percentage: bool = False, smallest: bool = False, sort_count: int = 5):
    """
    Print the largest or smallest y values from a Series like object.

    Args:
        title: Label printed above the output.
        x: Pandas Series (or Series like) supporting `.nlargest()` / `.nsmallest()`.
        as_percentage: If True, format values as percentages (x * 100) with 2 decimals.
        sort_count: Number of values to return.
        smallest: If True, print the smallest y values instead of the largest y values.

    Returns:
        None (prints to console).
    """
    if smallest == False:
        printed = x.nlargest(sort_count)
        which_end = f"Largest {sort_count}"
    else:
        printed = x.nsmallest(sort_count)
        which_end = f"Smallest {sort_count}"
    
    print(f"\n{title} ({which_end}):")

    if as_percentage == True:
        print(f"\n{(printed * 100).round(2).astype(str) + "%"}")
    else:
        print(f"\n{printed.round(4)}")

def get_sorted(x, sort_count: int = 5, smallest: bool = False):
    """
    Return the largest or smallest N values from a Series like object.

    Args:
        x: Pandas Series (or Series like) supporting `.nlargest()` / `.nsmallest()`.
        sort_count: Number of values to return.
        smallest: If True, return the smallest values instead of the largest.

    Returns:
        A Series of the top/bottom `sort_count` values.
    """
    if smallest == False:
        values = x.nlargest(sort_count)
    else:
        values = x.nsmallest(sort_count)
    
    return values

# ----------------------------------------------------------
print(f"\n---------- PHASE 1: LOAD / FETCH DATA ----------")
# ----------------------------------------------------------

# ---------- LOAD TICKERS FROM CSV LIST ----------

ticker_files = ["US Equity Tickers (Market Cap > $10B USD).csv"]

def load_tickers(ticker_files: str):
    """
    Load ticker/name pairs from multiple no header CSV files and return a {ticker: name} dict.

    Expects each CSV to have at least two columns:
    column 0 = ticker, column 1 = name. Values are stripped of whitespace.

    Args:
        ticker_files: Iterable of CSV filenames located in specified file path.

    Returns:
        dict[str, str]: Mapping of ticker symbols to names.
    """
    tickers_df = pd.concat(pd.read_csv(f"/Users/emmanuelbutterworth/Desktop/Tickers/{i}", header = None) for i in ticker_files)

    tickers = dict(zip(
        tickers_df[0].astype(str).str.strip(), 
        tickers_df[1].astype(str).str.strip()))
    
    return tickers

tickers = load_tickers(ticker_files)

# ---------- LOAD IN / FETCH RAW PRICE DATA ----------

def fetch_raw_close_price_data(file_path: str, tickers: dict[str, str], time_interval: str, time_period: str):
    """
    Download historical close price data from Yahoo Finance for the given tickers
    and save it to a CSV.

    Run this once to fetch and store the data, then use `load_raw_price_data` afterward to
    read the saved CSV instead of downloading again.

    Args:
        file_path: Where to save the CSV (full path + filename).
        tickers: {ticker_symbol: company_name}. Only the ticker symbols (keys) are used.
        time_period: yfinance period (e.g. 'ytd', '1y', '6mo')
        time_interval: yfinance interval (e.g. '1d', '1h', '30m').

    Notes:
        Uses adjusted prices (auto_adjust=True).
    """
    raw_price_data = yf.download(
        list(tickers.keys()),
        period = time_period,
        interval = time_interval,
        group_by = "ticker",
        auto_adjust = True,
        threads = False)

    raw_price_close_data = raw_price_data.xs("Close", axis=1, level=1).rename(columns=tickers)
    raw_price_close_data.to_csv(file_path)

def load_raw_price_data(file_path: str):
    """
    Load saved price data from a CSV file into a pandas DataFrame.

    Args:
        file_path: Full path to the CSV file.

    Returns:
        A DataFrame indexed by Date with price data columns.
    """
    raw_price_data = pd.read_csv(file_path, parse_dates = ["Date"], index_col = "Date")
    return raw_price_data

if download_data == True:
    fetch_raw_close_price_data(raw_price_data_file_path, tickers, raw_price_data_interval, raw_price_data_period)
    raw_price_data = load_raw_price_data(raw_price_data_file_path).dropna(axis=1, how="any")
    print("\n RAW CLOSE PRICE DATA FETCHED")
else:
    raw_price_data = load_raw_price_data(raw_price_data_file_path).dropna(axis=1, how="any")
    printx("RAW PRICE DATA LOADED", raw_price_data)

# -------------------------------------------------------------------------
print(f"\n---------- PHASE 2: SCREEN UNIVERSE VIA SHARPE RATIO ----------")
# -------------------------------------------------------------------------

# ---------- FIND RETURNS FROM RAW PRICE DATA ----------

def get_returns(raw_price_data: pd.DataFrame):
    """
    Return simple percentage returns from a price DataFrame.
    """
    returns = raw_price_data.pct_change()
    return returns

returns = get_returns(raw_price_data)
printx("RETURNS", returns, True)

# ---------- FIND AVERAGE & STD OF RETURNS ----------

average_returns = returns.mean()
print_sorted("AV. RETURNS", average_returns, True)

std_returns = returns.std()
print_sorted("STD RETURNS", std_returns, True, True)

# ---------- FIND ANNUALISED RETURNS ----------

def get_annualised_returns(average_returns: pd.DataFrame, interval: str = raw_price_data_interval):
    """
    Convert average periodic returns into annualised returns.

    Args:
        average_returns: Average returns for each asset/column for the given period.
        interval: Return frequency, one of {"1d", "1wk", "1mo"}.

    Returns:
        Annualised returns with the same shape as `average_returns`.
    """
    if interval == "1d":
        annualised_returns = (average_returns+1)**252 - 1

    elif interval == "1wk":
        annualised_returns = (average_returns+1)**52 - 1

    elif interval == "1mo":
        annualised_returns = (average_returns+1)**12 - 1

    return annualised_returns

annualised_returns = get_annualised_returns(average_returns)
print_sorted("ANNUALISED RETURNS", annualised_returns, True)

# ---------- FIND ANNUALISED STD ----------

def get_annualised_std(std_returns: pd.DataFrame, interval: str = raw_price_data_interval):
    """
    Annualise return standard deviation (volatility) from a given frequency.

    Args:
        std_returns: Standard deviation of returns at the given frequency.
        interval: Return frequency, one of {"1d", "1wk", "1mo"}.

    Returns:
        Annualised standard deviation (volatility) with the same shape as `std_returns`.
    """
    if interval == "1d":
        annualised_std = std_returns * np.sqrt(252)

    elif interval == "1wk":
        annualised_std = std_returns * np.sqrt(52)

    elif interval == "1mo":
        annualised_std = std_returns * np.sqrt(12)

    return annualised_std

annualised_std = get_annualised_std(std_returns)
print_sorted("ANNUALISED STD", annualised_std, True, True)

# ---------- FIND ANNUAL SHARPE ----------

def get_annual_sharpe(annualised_returns: pd.DataFrame, annualised_std: pd.DataFrame, rf: float):
    """
    Compute the annual Sharpe ratio for each asset/column.

    Args:
        annualised_returns: Annualised returns.
        annualised_std: Annualised standard deviation (volatility).
        rf: Annual risk free rate (as a decimal).

    Returns:
        Sharpe ratio values with the same shape as `annualised_returns`.
    """
    annual_sharpe = (annualised_returns - rf)/annualised_std
    return annual_sharpe

annual_sharpe = get_annual_sharpe(annualised_returns, annualised_std, rf)
print_sorted("ANNUAL SHARPE", annual_sharpe)

# ---------- SORT TOP N ANNUAL SHARPE ----------

selected_assets = get_sorted(annual_sharpe, portfolio_assets_considered)
selected_assets_returns = returns.loc[:, selected_assets.index].copy()
selected_assets_prices = raw_price_data.loc[:, selected_assets.index].copy()

# ---------- PLOT TOP N ANNUAL SHARPE ----------

def plot_sharpe(annual_sharpe: pd.Series, top_n: int = portfolio_assets_considered):
    s = annual_sharpe.dropna().sort_values(ascending = False)

    plt.figure(figsize=(10, 5))
    s.head(top_n).sort_values().plot(kind="barh")
    plt.title(f"Top {top_n} Assets by Annual Sharpe")
    plt.xlabel("Annual Sharpe")
    plt.grid(True, alpha = 0.3)
    plt.tight_layout()
    plt.show()

#plot_sharpe(annual_sharpe, top_n=portfolio_assets_considered)

# -----------------------------------------------------------------------------------------------------
print(f"\n---------- PHASE 3: OPTIMISE WEIGHTS FOR GLOBAL MINIMUM VARIANCE (GMV) PORTFOLIO ----------")
# -----------------------------------------------------------------------------------------------------

# ---------- COMPUTE COVARIANCE MATRIX ----------

selected_assets_covariance_matrix = (selected_assets_returns.cov()) * 252
printx("SELECTED ASSETS COV. MATRIX",selected_assets_covariance_matrix)

# ---------- PLOT COVARIANCE MATRIX ----------

def plot_selected_covariance_heatmap(selected_assets_covariance_matrix: pd.DataFrame, title: str = "Selected Assets Annualised Covariance Matrix",): 
    
    cov = selected_assets_covariance_matrix.copy()

    plt.figure(figsize=(10, 8))
    plt.imshow(cov.values, aspect="auto")
    plt.title(title)
    plt.xticks(range(cov.shape[1]), cov.columns, rotation=90, fontsize=7)
    plt.yticks(range(cov.shape[0]), cov.index, fontsize=7)
    plt.colorbar(label="Covariance")
    plt.tight_layout()
    plt.show()

#plot_selected_covariance_heatmap(selected_assets_covariance_matrix)

# ---------- ANNUAL RETURN & STD FOR SELECTED ASSETS ----------

selected_assets_annualised_returns = get_annualised_returns(selected_assets_returns.mean())
printx("SELECTED ASSETS ANN. RETURN", selected_assets_annualised_returns, True)

selected_assets_annualised_vol = get_annualised_std(selected_assets_returns.std())
printx("SELECTED ASSETS ANN. VOL", selected_assets_annualised_vol, True)

# ---------- PORTFOLIO WEIGHTS AND ALLOCATIONS ----------

def get_portfolio_return(weights, returns):
    """
    Compute portfolio return from asset weights and asset returns.

    Args:
        weights: Portfolio weights (1D array/Series or column vector).
        returns: Asset returns (vector of returns aligned to `weights`).

    Returns:
        Portfolio return as a scalar.
    """
    return weights.T @ returns

def get_portfolio_vol(weights, covariance_matrix):
    """
    Compute portfolio volatility given weights and a covariance matrix.

    Args:
        weights: Portfolio weights (1D array/Series or column vector).
        covariance_matrix: Asset return covariance matrix aligned to `weights`.

    Returns:
        Portfolio volatility (standard deviation) as a scalar.
    """
    return ((weights.T @ covariance_matrix @ weights) ** 0.5)

def get_max_sharpe_ratio_weights(rf, expected_return, covariance_matrix):
    """
    Finds the portfolio weights whihc maximise the Sharpe ratio (long only, fully invested).

    Uses SLSQP to minimise the negative Sharpe ratio subject to:
        - sum(weights) = 1
        - 0 <= weight_i <= 1 for all assets

    Args:
        rf: Risk free rate (same frequency as `expected_return`).
        expected_return: Expected returns vector of shape (n,).
        covariance_matrix: Covariance matrix of shape (n, n).

    Returns:
        Optimised weights as a 1D NumPy array of length n.

    Notes:
        No shorting or leverage is allowed.
    """
    number_assets = expected_return.shape[0]
    initial_guess = np.repeat(1/number_assets, number_assets)
    bounds = ((0.0, 1.0),) * number_assets

    weights_sum_to_1 = {'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1}
    
    def negative_sharpe(weights, rf, expected_return, covariance_matrix):
        """
        Compute the negative Sharpe ratio (as a minimisation objective).

        Args:
            weights: Portfolio weights.
            rf: Risk free rate (same frequency as `expected_return`).
            expected_return: Expected returns vector aligned to `weights`.
            covariance_matrix: Covariance matrix aligned to `weights`.

        Returns:
            Negative Sharpe ratio as a scalar.
        """
        returns = get_portfolio_return(weights, expected_return)
        volatility = get_portfolio_vol(weights, covariance_matrix)
        return -(returns - rf)/volatility
    
    weights = minimize(negative_sharpe, initial_guess,
                       args = (rf, expected_return, covariance_matrix), method='SLSQP',
                       options = {'disp': False},
                       constraints = (weights_sum_to_1,),
                       bounds = bounds)
    
    return weights.x

def get_global_minimum_variance_weights(covariance_matrix: pd.DataFrame):
    """
    Compute long only Global Minimum Variance (GMV) portfolio weights.

    This leverages `get_max_sharpe_ratio_weights` by setting rf = 0 and using a
    constant expected return vector. With equal expected returns, maximising
    Sharpe becomes equivalent to minimising portfolio variance under the
    fully invested, long only constraints.

    Args:
        covariance_matrix: Asset return covariance matrix (n x n), its index is used to label the output weights.

    Returns:
        A DataFrame of GMV weights indexed by the asset names.
    """
    number_assets = covariance_matrix.shape[0]
    return pd.DataFrame(get_max_sharpe_ratio_weights(0, np.repeat(1, number_assets), covariance_matrix), index = covariance_matrix.index)

portfolio_weights = get_global_minimum_variance_weights(selected_assets_covariance_matrix)
print(f"\n ----- PORTFOLIO WEIGHTS ----- ")
print("\n" + ((portfolio_weights * 100).round(2).astype(str) + "%").to_string())

portfolio_allocations = initial_capital * portfolio_weights
print(f"\n ----- PORTFOLIO ALLOCATIONS ----- ")
print(("$" + portfolio_allocations.round(2).astype(str)).to_string())

# ---------- PLOT PORTFOLIO WEIGHTS AND ALLOCATIONS ----------

def plot_portfolio_weights_pie(
    portfolio_weights: pd.DataFrame,
    min_slice: float = 0.01,   
    pct_label_min: float = 0.03,
    donut: bool = True,
    title: str = "Portfolio Weights"):

    w = portfolio_weights.iloc[:, 0].astype(float).copy()

    big = w[w >= min_slice].sort_values(ascending=False)
    small = w[w < min_slice]

    if small.sum() > 0:
        big.loc["Other"] = small.sum()

    labels = big.index.tolist()
    values = big.values

    def autopct(p):
        return f"{p:.1f}%" if (p / 100) >= pct_label_min else ""

    fig, ax = plt.subplots(figsize=(10, 6))

    wedgeprops = dict(edgecolor="white", linewidth=1)
    if donut:
        wedgeprops["width"] = 0.45  

    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,               
        autopct=autopct,
        startangle=90,
        counterclock=False,
        pctdistance=0.75,
        wedgeprops=wedgeprops,
        textprops={"fontsize": 10},
    )

    ax.set_title(title)
    ax.axis("equal")

    ax.legend(
        wedges,
        labels,
        title="Holdings",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=False,
        fontsize=9,
        title_fontsize=10,
    )

    plt.tight_layout()
    plt.show()

#plot_portfolio_weights_pie(portfolio_weights)

# ---------- FIND EXPECTED RETURN & VOL OF PORTFOLIO ----------

portfolio_expected_return = get_portfolio_return(portfolio_weights, selected_assets_annualised_returns)
printx("PORTFOLIO EXPECTED RETURN (ANNUAL)", portfolio_expected_return.iloc[0], True)

portfolio_expected_vol = get_portfolio_vol(portfolio_weights, selected_assets_covariance_matrix)
printx("PORTFOLIO EXPECTED VOL. (ANNUAL)", portfolio_expected_vol.iloc[0,0], True)

portfolio_sharpe = get_annual_sharpe(portfolio_expected_return, portfolio_expected_vol, rf)
printx("PORTFOLIO SHARPE (ANNUAL)", portfolio_sharpe.iloc[0,0])

# ---------- PLOT PORTFOLIO VS BENCHMARKS VALUE OVER TIME ----------

def get_portfolio_and_benchmark_values():

    # --- Portfolio value ---
    weights = portfolio_weights.iloc[:, 0]
    prices = selected_assets_prices.copy()
    norm = prices / prices.iloc[0]
    portfolio_value = initial_capital * norm.mul(weights, axis=1).sum(axis=1)

    # --- Benchmarks ---
    bench_cols = [b for b in benchmarks if b in raw_price_data.columns]

    bench_prices = raw_price_data[bench_cols].copy()
    bench_norm = bench_prices / bench_prices.iloc[0]
    bench_values = initial_capital * bench_norm

    combined = pd.concat([portfolio_value.rename("Portfolio"), bench_values], axis=1)
    return combined

portfolio_vs_benchmark_values = get_portfolio_and_benchmark_values()

def portfolio_vs_benchmark_value_plot(values_df: pd.DataFrame):
    """
    Plot Portfolio + benchmark value series.
    """
    plt.figure(figsize=(10, 5))
    values_df.plot(ax=plt.gca())
    plt.title(f"Portfolio vs Benchmarks ({raw_price_data_period})")
    plt.xlabel("Date")
    plt.ylabel("Value ($)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

portfolio_vs_benchmark_value_plot(portfolio_vs_benchmark_values)

# ---------- PLOT PORTFOLIO VS BENCHMARKS STD ----------

def portfolio_vs_benchmark_std_plot():

    names = ["Portfolio"] + benchmarks

    values = [float(np.asarray(portfolio_expected_vol).squeeze())]
    values += [float(annualised_std[b]) for b in benchmarks]

    plt.figure(figsize=(10, 4))
    plt.bar(names, values)
    plt.title("Annual Volatilities")
    plt.ylabel("Annual Volatility")
    plt.xticks(rotation=25, ha="right")
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.show()

portfolio_vs_benchmark_std_plot()

# ---------- PLOT PORTFOLIO VS BENCHMARKS SHARPE ----------

def portfolio_vs_benchmark_sharpe_plot():

    names = ["Portfolio"] + benchmarks

    values = [float(np.asarray(portfolio_sharpe).squeeze())]
    values += [float(annual_sharpe[b]) for b in benchmarks]

    plt.figure(figsize=(10, 4))
    plt.bar(names, values)
    plt.title("Sharpe Ratios")
    plt.ylabel("Annual Sharpe")
    plt.xticks(rotation=25, ha="right")
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.show()

portfolio_vs_benchmark_sharpe_plot()

# ---------- CONSTANT PROPORTION PORTFOLIO INSURANCE ----------

def cppi_weights(portfolio_value: float, floor: float, multiplier: float):
    """
    Returns (w_risky, w_safe) for CPPI.

    portfolio_value: current total value
    floor: minimum protected value
    multiplier: CPPI multiplier
    max_risky: cap on risky weight (1 = no leverage)
    """
    cushion = max(portfolio_value - (floor), 0) / portfolio_value
    w_risky = multiplier * cushion
    w_risky = min(max(w_risky, 0), 1)
    w_safe = 1 - w_risky
    return w_risky, w_safe

w_risky, w_safe = cppi_weights(current_capital, cppi_floor, cppi_multiplier)

portfolio_cppi_allocations = w_risky * portfolio_allocations

print(f"\n ----- PORTFOLIO CPPI ALLOCATIONS ----- ")
print(f"\n Risky: {w_risky:.2%}, Safe: {w_safe:.2%}")
print(("$" + portfolio_cppi_allocations.round(2).astype(str)).to_string())
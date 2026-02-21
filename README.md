# Sharpe-Filtered-Minimum-Variance-Portfolio-Investment-Strategy
This script implements a Sharpe filtered minimum variance portfolio strategy by moving from a broad US equity universe (Market Cap > $10B USD) to an optimised, long only portfolio, then layering a simple CPPI sizing rule on top, with weekly CPPI resizing, and monthly portfolio reconstruction. It begins by defining key controls, including the data window and frequency, the initial capital, the annual risk free rate, the number of assets to retain after screening, and the CPPI floor and multiplier. A set of benchmark series is also specified for later comparison, with the expectation that these benchmarks exist as named columns in the loaded price dataset.

It then loads ticker and name pairs from CSV files to form a universe dictionary, which is used both to download prices and to label outputs clearly. Depending on the download flag, the program either fetches adjusted close prices from Yahoo Finance or loads an existing CSV from disk. After loading, it removes any assets with missing values over the sample to ensure a complete price panel.

Next, the strategy converts prices into simple daily returns and computes each asset’s mean return and standard deviation. These are annualised, and an annual Sharpe ratio is calculated for every asset as excess annual return over annual volatility. The universe is screened by selecting the top n assets with the highest Sharpe ratios, and only these assets prices and returns are carried forward.

<p align="center">
  <img width="2000" height="1494" alt="1" src="https://github.com/user-attachments/assets/c05f667a-8db0-4891-a8f7-515d2f462d40" />
  <br>
  <em><b>Figure 1.</b> Residual (spread) time series for a qualified tradable pair, with equilibrium level shown as a dashed line.</em>
</p>

<br>

With the screened set, the program computes the annualised covariance matrix and uses it to build a Global Minimum Variance portfolio under long only, fully invested constraints. Rather than directly minimising variance, it reuses a Sharpe maximisation optimiser by setting the risk free rate to zero and assigning equal expected returns to all assets, making the optimisation equivalent to minimising volatility. The resulting weights are printed and converted into dollar allocations, with visualisations such as a covariance heatmap and a donut chart of portfolio weights.

<p align="center">
  <img width="976" height="804" alt="2" src="https://github.com/user-attachments/assets/2f1a313e-b298-4cc7-879d-b6b6815b8cd0" />
  <br>
  <em><b>Figure 2.</b> Residual (spread) time series for a qualified tradable pair, with equilibrium level shown as a dashed line.</em>
</p>

<br>

<p align="center">
  <img width="2000" height="1198" alt="3" src="https://github.com/user-attachments/assets/573f8f0f-5f4a-418f-a17a-0f67cb9927e2" />
  <br>
  <em><b>Figure 3.</b> Residual (spread) time series for a qualified tradable pair, with equilibrium level shown as a dashed line.</em>
</p>

<br>

Finally, the script reports portfolio expected return, volatility, and Sharpe ratio, then constructs a portfolio value series by normalising asset prices to their starting values and applying the fixed weights to produce a buy and hold style portfolio path. Benchmark value series are built similarly where available, and the portfolio is plotted against benchmarks alongside volatility and Sharpe bar charts. A CPPI function is then applied as a snapshot sizing overlay, calculating risky and safe weights from the current portfolio value relative to the floor, and outputting the implied risky allocation to the optimised portfolio.

<p align="center">
  <img width="2000" height="996" alt="4" src="https://github.com/user-attachments/assets/3256731b-9077-4b15-944e-ece001a8b0b0" />
  <br>
  <em><b>Figure 4.</b> Residual (spread) time series for a qualified tradable pair, with equilibrium level shown as a dashed line.</em>
</p>

<br>

<p align="center">
  <img width="1998" height="844" alt="5" src="https://github.com/user-attachments/assets/c49b4925-8e78-44b1-879b-79a0784bfe7d" />
  <br>
  <em><b>Figure 5.</b> Residual (spread) time series for a qualified tradable pair, with equilibrium level shown as a dashed line.</em>
</p>

<br>

<p align="center">
  <img width="1998" height="1234" alt="6" src="https://github.com/user-attachments/assets/8f58c288-25bc-4645-b17e-a4c32d8ead8e" />
  <br>
  <em><b>Figure 6.</b> Residual (spread) time series for a qualified tradable pair, with equilibrium level shown as a dashed line.</em>
</p>

<br>

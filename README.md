# Sharpe-Filtered-Minimum-Variance-Portfolio-Investment-Strategy
Builds a Sharpe filtered minimum variance, long only US equity portfolio. Loads/downloads prices, drops missing data, computes returns and annual Sharpe, keeps top n, then solves a GMV optimisation (via Sharpe optimiser with rf=0). Plots vs benchmarks and applies a CPPI floor/multiplier to size risky vs safe.

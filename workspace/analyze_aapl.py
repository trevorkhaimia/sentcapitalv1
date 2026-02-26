import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Download AAPL data
aapl = yf.download('AAPL', start='2020-01-01', end='2023-01-01')

# Calculate daily returns
aapl['Daily Return'] = aapl['Adj Close'].pct_change()

# Calculate volatility (annualized)
volatility = aapl['Daily Return'].std() * np.sqrt(252)

# Calculate Sharpe Ratio (assuming risk-free rate = 0)
sharpe_ratio = aapl['Daily Return'].mean() / aapl['Daily Return'].std() * np.sqrt(252)

# Plot trends
plt.figure(figsize=(14, 7))
plt.plot(aapl['Adj Close'], label='AAPL Adjusted Close Price')
plt.title('AAPL Stock Price Trend')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

# Print results
print(f"Volatility: {volatility:.4f}")
print(f"Sharpe Ratio: {sharpe_ratio:.4f}")
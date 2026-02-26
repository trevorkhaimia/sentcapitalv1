import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_volatility(daily_returns):
    return daily_returns.std() * np.sqrt(252)

def calculate_sharpe_ratio(daily_returns):
    return (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)

def download_and_analyze_data(ticker):
    data = yf.download(ticker, start='2020-01-01', end='2023-01-01')
    data['Daily Return'] = data['Adj Close'].pct_change()
    return data

def plot_price_trend(data, ticker):
    plt.figure(figsize=(14, 7))
    plt.plot(data['Adj Close'], label=f'{ticker} Price')
    plt.title(f'{ticker} Stock Price Trend')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

def print_metrics(volatility, sharpe_ratio, ticker):
    print(f"\n{ticker} Metrics:")
    print(f"Annualized Volatility: {volatility:.4f}")
    print(f"Sharpe Ratio: {sharpe_ratio:.4f}")

def analyze_stock(ticker='AAPL'):
    data = download_and_analyze_data(ticker)
    volatility = calculate_volatility(data['Daily Return'].dropna())
    sharpe_ratio = calculate_sharpe_ratio(data['Daily Return'].dropna())
    print_metrics(volatility, sharpe_ratio, ticker)
    plot_price_trend(data, ticker)
    return {'volatility': volatility, 'sharpe_ratio': sharpe_ratio}

if __name__ == '__main__':
    analyze_stock()
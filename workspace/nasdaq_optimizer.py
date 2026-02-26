import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from scipy.optimize import minimize

def get_nasdaq_tickers():
    url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[1].text.strip()
        tickers.append(ticker)
    return tickers

def download_stock_data(tickers):
    data = yf.download(tickers, start=pd.Timestamp.now() - pd.DateOffset(years=1), end=pd.Timestamp.now())['Adj Close']
    return data

def calculate_returns(data):
    returns = data.pct_change().dropna()
    annual_returns = returns.mean() * 252
    annual_volatility = returns.std() * np.sqrt(252)
    sharpe_ratios = annual_returns / annual_volatility
    return returns, annual_returns, annual_volatility, sharpe_ratios

def find_top_performers(sharpe_ratios, n=20):
    top_performers = sharpe_ratios.sort_values(ascending=False).head(n)
    return top_performers.index.tolist()

def optimize_portfolio(returns, tickers):
    cov_matrix = returns.cov()
    
    def portfolio_stats(weights):
        port_return = np.sum(returns.mean() * weights) * 252
        port_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
        sharpe = port_return / port_volatility
        return -sharpe
    
    num_assets = len(tickers)
    args = (returns,)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0,1) for asset in range(num_assets))
    initial_weights = np.array(num_assets * [1./num_assets])
    
    optimized = minimize(portfolio_stats, initial_weights, method='SLSQP', 
                         bounds=bounds, constraints=constraints)
    return optimized.x

def plot_performance(portfolio, optimized_weights, tickers):
    plt.figure(figsize=(14,7))
    portfolio['Adj Close'].plot(label='Portfolio Performance', linewidth=2)
    portfolio['Optimized Portfolio'] = np.sum(portfolio[tickers] * optimized_weights, axis=1)
    portfolio['Optimized Portfolio'].plot(label='Optimized Portfolio', linewidth=2)
    plt.title('Portfolio Performance vs Optimized Portfolio')
    plt.xlabel('Date')
    plt.ylabel('Normalized Price')
    plt.legend()
    plt.show()

def analyze_portfolio():
    tickers = get_nasdaq_tickers()
    stock_data = download_stock_data(tickers)
    returns, annual_returns, annual_volatility, sharpe_ratios = calculate_returns(stock_data)
    
    top_tickers = find_top_performers(sharpe_ratios)
    top_data = stock_data[top_tickers]
    top_returns = returns[top_tickers]
    
    optimized_weights = optimize_portfolio(top_returns, top_tickers)
    weights_df = pd.DataFrame({'Ticker': top_tickers, 'Weight': optimized_weights})
    weights_df = weights_df.sort_values(by='Weight', ascending=False)
    
    initial_port = top_data.iloc[0].values
    portfolio = top_data.div(initial_port).mul(100)
    
    print("\nTop Performers based on Sharpe Ratio:")
    print(sharpe_ratios[top_tickers].sort_values(ascending=False))
    print("\nOptimized Portfolio Weights:")
    print(weights_df)
    
    plot_performance(portfolio, optimized_weights, top_tickers)
    
    return weights_df

if __name__ == '__main__':
    analyze_portfolio()
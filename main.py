import datetime as dt
import pandas as pd
import numpy as np
from pandas_datareader import data as pdr

start = dt.datetime(2021, 1, 1) # start 
end = dt.datetime.now()

stockList = ['AAPL', 'T', 'BAC', 'AMZN'] # tickers
stocks = ['SPY'] + [i for i in stockList]

df = pdr.get_data_yahoo(stocks, start, end)
log_returns = np.log(df.Close / df.Close.shift(1)).dropna()


def calc_beta(df):
    np_array = df.values
    # Market index is the first column 0
    m = np_array[:, 0]
    beta = []
    for ind, col in enumerate(df):
        if ind > 0:
            # stock returns are indexed by ind
            s = np_array[:, ind]
            # Calculate covariance matrix between stock and market
            covariance = np.cov(s, m)
            beta.append(covariance[0, 1] / covariance[1, 1])
    return pd.Series(beta, df.columns[1:], name='Beta')


beta = calc_beta(log_returns)

units = np.array([100, 250, 300, 400]) # weights
prices = df.Close[-1:].values.tolist()[0]
price = np.array([round(price, 2) for price in prices[1:]])
value = [unit * pr for unit, pr in zip(units, price)]
weight = [round(val / sum(value), 2) for val in value]
beta = round(beta, 2)
Portfolio = pd.DataFrame({
    'Stock': stockList,
    'Direction': 'Long',
    'Type': 'S',
    'Stock Price': price,
    'Price': price,
    'Units': units,
    'Value': units * price,
    'Weight': weight,
    'Beta': beta,
    'Weighted Beta': weight * beta
})

Portfolio = Portfolio.drop(['Weight', 'Weighted Beta'], axis=1)
Portfolio['Delta'] = Portfolio['Units']

# Options = [{'option': 'CBA0Z8', 'underlying': 'CBA', 'price': 3.950, 'units': 2, 'delta': 0.627, 'direction': 'Short',
#             'type': 'Call'}
#            ]
# for index, row in enumerate(Options):
#     Portfolio.loc[row['option']] = [row['underlying'], row['direction'], row['type'],
#                                     Portfolio.loc[row['underlying'], 'Price'],
#                                     row['price'], row['units'], row['price'] * row['units'] * 100,
#                                     beta[row['underlying']],
#                                     (row['delta'] * row['units'] * 100 if row['direction'] == 'Long' else -row[
#                                         'delta'] * row['units'] * 100)]

Portfolio['SPY Weighted Delta'] = round(
    Portfolio['Beta'] * (Portfolio['Stock Price'] / prices[0]) * Portfolio['Delta'], 2)
Portfolio['SPY Weighted Delta 1%'] = round(Portfolio['Beta'] * (Portfolio['Stock Price']) * Portfolio['Delta'] * 0.01,
                                           2)

Portfolio.loc['Total', ['Value', 'SPY Weighted Delta', 'SPY Weighted Delta 1%']] \
    = Portfolio[['Value', 'SPY Weighted Delta', 'SPY Weighted Delta 1%']].sum()

print(Portfolio)

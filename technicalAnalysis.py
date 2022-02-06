# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 17:47:03 2022

@author: Kaletho

Following tutorial from "How to invest with data science"
https://www.youtube.com/watch?v=4jaBKXDqg9U

This file calculates and plots Bollinger and Ichimoku
(Also calculates daily and cumulative return)

The output of this file is a list of stocks 
"""

# Data management
import numpy as np
import pandas as pd

# For plotting 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates # for styling dates

from plotly.offline import plot # Trying to make it work with Spyder
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import cufflinks as cf # an addon to plotly
# Use plotly locally
cf.go_offline()

# For webscrapping yahoo finance
import yfinance as yf # need to read what this does and how
# https://github.com/ranaroussi/yfinance

# For managing files
import time
import datetime as dt
import os
from os import listdir
from os.path import isfile, join

# For managing warnings
import warnings
warnings.simplefilter("ignore")

# CONSTANTS
# PATH = "D:\\webScrapping\\yfinance\\usdcop\\" # need to use \\ for windows
PATH = "D:\\webScrapping\\derekBanasTutorial\\wilshire_top\\"
stocks_path = "D:\\webScrapping\\derekBanasTutorial\\wilshire_stocks\\"

# Start & end dates default
S_DATE = '2017-06-19'
E_DATE = '2018-06-19'
S_DATE_DT = pd.to_datetime(S_DATE)
E_DATE_DT = pd.to_datetime(E_DATE)

risk_free_rate = 0.0125 # Approximate 10 year bond rate
# could also be CDT rates in Colombia
# a rate to beat?

# GET COLUMN DATA FROM CSV
# def get_column_from_csv(file, col_name):
#     # If file does not exist, issue a warning
#     try:
#         df = pd.read_csv(file)
#     except FileNotFoundError:
#         print("File doesn't exist")
#     else:
#         return df[col_name]
    
# GET TICKERS FROM DOWNLOADED STOCK FILES
files = [x for x in listdir(stocks_path) if isfile(join(stocks_path, x))] 
tickers = [os.path.splitext(x)[0] for x in files] # split file extension 
tickers.sort() # although they should be sorted by windows
print("There are ", len(tickers), " tickers")

# GET DATAFRAME FROM CSV
def get_stock_df_from_csv(ticker):
    try:
        df = pd.read_csv(stocks_path + ticker + '.csv', index_col=0)
        
        # Check if df has duplicate indexes
        # Sometimes yahoo data comes duplicated
        if not df.index.is_unique:
            df = df.loc[~df.index.duplicated(), :] # ~ is the "invert" or "complement" operation
            # is the bitwise complement operator in python which essentially calculates -x - 1
            
    except FileNotFoundError:
        print("File doesn't exist!")
    else:
        return df
        
# CALCULATE DAILY RETURNS AND ADD THEM AS A COLUMN
def add_daily_return_to_df(df):
    '''
    Shifting the df by 1 means looking the previous day's value
    This is a rate of return (percentage)
    (close + previous close)/ previous close
    '''
    df['daily_return'] = (df['Close'] / df['Close'].shift(1)) - 1
    return df

# CALCULATE CUMULATIVE RETURNS
def add_cumulative_return_to_df(df):
    '''
    The aggregate effect of price change, compounded (daily in my case)
    Cumprod returns cumulative product, i.e. it compounds
    '''
    df['cum_return'] = (1 + df['daily_return']).cumprod()
    return df
    
# ADD BOLLINGER BANDS
# Basically a moving average line and a band showing the standard deviation
def add_bollinger_bands(df):
    df['middle_band'] = df['Close'].rolling(window=20).mean() # Consider using 22D to work in days
    df['upper_band'] = df['middle_band'] + 1.96 * df['Close'].rolling(window=20).std()
    df['lower_band'] = df['middle_band'] - 1.96 * df['Close'].rolling(window=20).std()
    return df

# ADD ICHIMOKU DATA TO DATAFRAME
def add_ichimoku(df):
    '''
    My personal view: This is just averaging the future using the past. Averaging!
    It provides information on momentum, support and resistance. It is made up of 5 lines:
    - Conversion Line (Tenkan-sen) : Represents support, resistance and reversals. Used to measure short term trends.
    - Baseline (Kijun-sen) : Represents support, resistance and confirms trend changes. Allows you to evaluate the strength of medium term trends. Called the baseline because it lags the price.
    - Leading Span A (Senkou A) : Used to identify future areas of support and resistance
    - Leading Span B (Senkou B) : Other line used to identify suture support and resistance
    - Lagging Span (Chikou) : Shows possible support and resistance. It is used to confirm signals obtained from other lines.
    - Cloud (Kumo) : Space between Span A and B. Represents the divergence in price evolution.

    A session is a day
    Formulas also from: https://www.investopedia.com/terms/i/ichimoku-cloud.asp
    '''
    hi26 = df['High'].rolling(window=26).max()
    hi52 = df['High'].rolling(window=52).max()
    
    lo26 = df['Low'].rolling(window=26).min()
    lo52 = df['Low'].rolling(window=52).min()
    
    # Conversion line = (Highest Value in period + Lowest value in period)/2 (9 sessions)
    df['conversion_line'] = 0.5 * (df['High'].rolling(window=9).max() + df['Low'].rolling(window=9).min())
    
    # Base line = (Highest Value in period + Lowest value in period)/2 (26 sessions)
    df['base_line'] = 0.5 * (hi26 + lo26)
    
    # Span A = (Conversion Value + Base Value)/2 (plot 26 Sessions into the future)
    df['span_A'] = (0.5 * (df['conversion_line'] + df['base_line'])).shift(26)
    
    # Span B = (Conversion Value + Base Value)/2 (plot 26 Sessions into the future)
    df['span_B'] = (0.5 * (hi52 + lo52)).shift(26)
        
    # Lagging Span = Price shifted back 26 periods
    df['lag_span'] = df['Close'].shift(-26)
    
    return df

# =============================================================================
# TRY ON ONE STOCK (check all the functions are working)
# ticker = 'AMD'
# try:
#     print('Working on ', ticker)
#     test_df = get_stock_df_from_csv(ticker)
#     test_df = add_daily_return_to_df(test_df)
#     test_df = add_cumulative_return_to_df(test_df)
#     # test_df = add_bollinger_bands(test_df)
#     test_df = add_ichimoku(test_df)
#     # test_df.to_csv(stocks_path + ticker + '.csv')
# except Exception as ex:
#     print(ex)

# =============================================================================

# PLOT BOLLINGER BANDS
def plot_with_bollinger_bands(df, ticker):
    fig = go.Figure()
    
    candle = go.Candlestick(x=df.index, open=df['Open'],
                            high=df['High'], low=df['Low'],
                            close=df['Close'], name='Candlestick')
    
    upper_line = go.Scatter(x=df.index, y=df['upper_band'],
                            line=dict(color='rgba(250, 0, 0, 0.75)', width=1),
                            name='Upper Band')
    
    mid_line = go.Scatter(x=df.index, y=df['middle_band'],
                            line=dict(color='rgba(0, 250, 0, 0.75)', width=1),
                            name='Middle Band')
    
    lower_line = go.Scatter(x=df.index, y=df['lower_band'],
                            line=dict(color='rgba(0, 0, 250, 0.75)', width=1),
                            name='Lower Band')
    
    fig.add_trace(candle)
    fig.add_trace(upper_line)
    fig.add_trace(mid_line)
    fig.add_trace(lower_line)
    
    fig.update_xaxes(title="Date", rangeslider_visible=True)
    fig.update_yaxes(title="Price")
    
    fig.update_layout(title=ticker+" Bollinger bands",
                      height=1200, width=1800, showlegend=True)
    
    plot(fig, auto_open=True)
    
# Let's try to plot ichimoku
# The plot should display a buy decision (green) or not (red)
def get_fill_color(label):
    if label >= 1:
        return 'rgba(0, 250, 0, 0.4)'
    else:
        return 'rgba(250, 0, 0, 0.4)'
    
def plot_ichimoku(df, ticker):
    candle = go.Candlestick(x=df.index, open=df['Open'],
                            high=df['High'], low=df['Low'],
                            close=df['Close'], name='Candlestick')
    
    df1 = df.copy()
    fig = go.Figure()
    df['label'] = np.where(df['span_A'] > df['span_B'], 1, 0) # condition for the color!!!
    
    df['group'] = df['label'].ne(df['label'].shift()).cumsum() # ne -> not equal
    # This last cumsum returns either a single True or False depending if 'label' changed value
    
    df = df.groupby('group') # group all those red or green zones
    
    dfs = [] # a list of dataframes
    for name, data in df:
        dfs.append(data)
        
    for df in dfs:
        fig.add_traces(go.Scatter(x=df.index, y=df.span_A,
                                  line=dict(color='rgba(0,0,0,0)')))
        fig.add_traces(go.Scatter(x=df.index, y=df.span_B,
                                  line=dict(color='rgba(0,0,0,0)'),
                                  fill='tonexty',
                                  fillcolor=get_fill_color(df['label'].iloc[0]))) # iloc -> finds where there are 0's
        
    baseline = go.Scatter(x=df1.index, y=df1['base_line'], 
                          line=dict(color='black', width=3), name='Baseline')
    
    conversion = go.Scatter(x=df1.index, y=df1['conversion_line'],
                            line=dict(color='blue', width=3), name='Conversion')
    
    lag = go.Scatter(x=df1.index, y=df1['lag_span'],
                            line=dict(color='#e09c00', width=2), name='Lag')
    
    span_a = go.Scatter(x=df1.index, y=df1['span_A'],
                            line=dict(color='red', width=2, dash='dot'), name='Span A')
    
    span_b = go.Scatter(x=df1.index, y=df1['span_B'],
                            line=dict(color='green', width=1, dash='dot'), name='Span B')
    
    fig.add_trace(candle)
    fig.add_trace(baseline)
    fig.add_trace(conversion)
    fig.add_trace(lag)
    fig.add_trace(span_a)
    fig.add_trace(span_b)
    
    fig.update_xaxes(title="Date", rangeslider_visible=True)
    fig.update_yaxes(title="Price")
    
    fig.update_layout(title = ticker, 
                      height=1200, width=1800, showlegend=True, 
                      plot_bgcolor = 'dimgray') # color from CSS colors list
    
    # plot(fig, auto_open=True)
    plot(fig, filename=PATH + ticker + '.html', auto_open=False)
    
# plot_with_bollinger_bands(test_df, ticker)
# plot_ichimoku(test_df, ticker)  

# ADD DAILY & CUMULATIVE GAINS TO DATAFRAMES
# To select the "best" later
# Uncomment when working with new stocks
# for t in tickers:
#     try:
#         print("Working on: ", t)
#         new_df = get_stock_df_from_csv(t)
#         new_df = add_daily_return_to_df(new_df)
#         new_df = add_daily_return_to_df(new_df)
#         new_df = add_cumulative_return_to_df(new_df)
#         new_df.to_csv(stocks_path + t + '.csv')
#     except Exeption as ex:
#         print(ex)
        

# =============================================================================

# GET SECTOR STOCKS
sec_df = pd.read_csv("D:\\webScrapping\\derekBanasTutorial\\big_stock_sectors.csv")

# indus_df = sec_df.loc[sec_df['Sector'] == "Industrial"]
# health_df = sec_df.loc[sec_df['Sector'] == "Healthcare"]
# it_df = sec_df.loc[sec_df['Sector'] == "Information Technology"]
# comm_df = sec_df.loc[sec_df['Sector'] == "Communication"]
# staple_df = sec_df.loc[sec_df['Sector'] == "Staples"]
# discretion_df = sec_df.loc[sec_df['Sector'] == "Discretionary"]
# utility_df = sec_df.loc[sec_df['Sector'] == "Utilities"]
# financial_df = sec_df.loc[sec_df['Sector'] == "Financials"]
# material_df = sec_df.loc[sec_df['Sector'] == "Materials"]
# restate_df = sec_df.loc[sec_df['Sector'] == "Real Estate"]
energy_df = sec_df.loc[sec_df['Sector'] == "Energy"]

# RETURN DF WITH CUMULATIVE RETURN FOR ALL STOCKS IN A SECTOR
def get_cum_ret_for_sector(sector_df):
    ticks = []
    cum_rets=[]
    
    for index, row in sector_df.iterrows():
        df = get_stock_df_from_csv(row['Ticker'])
        
        if df is None:
            pass
        else:
            ticks.append(row['Ticker'])
            
            cum = df['cum_return'].iloc[-1] 
            cum_rets.append(cum)
            
    return pd.DataFrame({'Ticker': ticks, 'CUM_RET': cum_rets})

# These below print "File doesn't exist!" from the get_stock_df_from_csv function
# because there are tickers from big_stock_sectors.csv that are not in the 
# downloaded stock data 
# industrial = get_cum_ret_for_sector(indus_df)
# health_care = get_cum_ret_for_sector(health_df)
# it = get_cum_ret_for_sector(it_df)
# commun = get_cum_ret_for_sector(comm_df)
# staples = get_cum_ret_for_sector(staple_df)
# discretion = get_cum_ret_for_sector(discretion_df)
# utility = get_cum_ret_for_sector(utility_df)
# finance = get_cum_ret_for_sector(financial_df)
# material = get_cum_ret_for_sector(material_df)
# restate = get_cum_ret_for_sector(restate_df)
energy = get_cum_ret_for_sector(energy_df)


# Look for stocks that would potentially make it into our portafolio
# TOP INDUSTRIAL
top = 10
# print("INDUSTRIAL")
# top_ind = industrial.sort_values(by=['CUM_RET'], ascending=False).head(top)
# print(top_ind)

# select one from those 10 and check it with ichimoku
def plot_ichi_top_10(top_sector_df):
    for t in top_sector_df['Ticker']:
        df_ind = get_stock_df_from_csv(t)
        df_ind = add_ichimoku(df_ind)
        plot_ichimoku(df_ind, t)
        time.sleep(2) # in seconds
        # they have to be opened slowly, otherwise my machine does not have enough
        # time to write them to disk/ram and open them again in the browser
        
# # TOP HEALTHCARE
# print("HEALTHCARE")
# top_health = health_care.sort_values(by=['CUM_RET'], ascending=False).head(top)
# print(top_health)

# # TOP IT
# print("IT")
# top_it = it.sort_values(by=['CUM_RET'], ascending=False).head(top)
# print(top_it)

# TOP COMMUNICATION
# print("COMMUNICATION")
# top_com = commun.sort_values(by=['CUM_RET'], ascending=False).head(top)
# print(top_com)

# # TOP STAPLES
# print("STAPLES")
# top_staples = staples.sort_values(by=['CUM_RET'], ascending=False).head(top)
# print(top_staples)

# # TOP DISCRETION
# print("DISCRETIONARY")
# top_discretion = discretion.sort_values(by=['CUM_RET'], ascending=False).head(top)
# print(top_discretion)

# # TOP UTLITY
# print("UTILITY")
# top_utility = utility.sort_values(by=['CUM_RET'], ascending=False).head(top)
# print(top_utility)

# # TOP FINANCE
# print("FINANCE")
# top_finance = finance.sort_values(by=['CUM_RET'], ascending=False).head(top)
# print(top_finance)

# # TOP MATERIALS
# print("FINANCE")
# top_materials = material.sort_values(by=['CUM_RET'], ascending=False).head(top)
# print(top_materials)

# # TOP REAL STATE
# print("REAL STATE")
# top_restate = restate.sort_values(by=['CUM_RET'], ascending=False).head(top)
# print(top_restate)

# # TOP ENERGY
print("ENERGY")
top_energy = energy.sort_values(by=['CUM_RET'], ascending=False).head(top)
print(top_energy)

# plot_ichi_top_10(top_ind)
# plot_ichi_top_10(top_health)
# plot_ichi_top_10(top_it)
# plot_ichi_top_10(top_com)
# plot_ichi_top_10(top_staples)
# plot_ichi_top_10(top_discretion)
# plot_ichi_top_10(top_utility)
# plot_ichi_top_10(top_finance)
# plot_ichi_top_10(top_materials)
# plot_ichi_top_10(top_restate)
plot_ichi_top_10(top_energy)

# Pick a handful of best-performing stocks and go to the next file: portfolio
# =============================================================================
# TAKE TRADES GIVEN THE BELOW CONDITIONS (IN THEIR ORDER)
# FIRST
# Price above cloud -> Take long trades
# Price below cloud -> Take short trades
# Price inside cloud -> Take no trades

# THEN
# When conversion crosses the baseline upwards, it's a long trading signal
# When conversion crosses the baseline downwards, it's a short trading signal

# FINALLY 
# If you're taking long trades, check that the lagging signal is above price
# Viceversa if you're taking short trades

# Exit signals
# When the lagging signal touches price
# When conversion crosses baseline again
# When the cloud touches price

# Stop loss can be set at the bottom/top of the cloud, when the position is taken

portfolio1 = ['ZNGA', 'VG', 'ADM', 'MKC', 'HSY', 'XEL', 'EXC', 'VRS', 'HCC',
              'BCC', 'WHD', 'OAS', 'EGY']

watch = ['CRC']

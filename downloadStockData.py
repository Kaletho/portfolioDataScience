# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 19:10:55 2022

@author: Kaletho

Following the "Download Every Stock in the World" tutorial from Derek Banas
https://www.youtube.com/watch?v=xzBcPoxue-g
"""

# Data management
import numpy as np
import pandas as pd

# For plotting 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates # for styling dates

# For managing files
import time
import datetime as dt

# For webscrapping yahoo finance
import yfinance as yf # need to read what this does and how
# https://github.com/ranaroussi/yfinance

# CONSTANTS
PATH = "D:\\webScrapping\\derekBanasTutorial\\"

# YFINANCE
def get_info_on_stock(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5y")
    # print(stock.info)
    
# get_info_on_stock('USDCOP=x')

def get_column_from_csv(file, col_name):
    '''
    Parameters
    ----------
    file : string
        path to file
    col_name : string
        column name

    Returns dataframe of column from csv file
    '''
    try:
        df = pd.read_csv(file)
    except FileNotFoundError:
        print("File not found")
    else:
        return df[col_name]
    
# GET STOCK TICKERS
# tickers = get_column_from_csv(PATH + 'NYSE.csv', 'Ticker')
tickers = get_column_from_csv(PATH + 'Wilshire-5000-Stocks.csv', 'Ticker')
# Wilshire: index of all equities that are actively traded in the United States
ntickers = len(tickers)
print('There are: ',  ntickers, 'tickers.')

# A LIST OF STOCKS TO BE DOWNLOADED
# they may be not yet downloaded or missing
stocks_not_downloaded = []
missing_stocks = []
# TODO err_msg = [] # save possible error messages from yfinance

def save_to_csv_from_yahoo(folder, ticker):
    stock = yf.Ticker(ticker)
    # yahoo finance datetimes are received as UTC.
    
    try:
        print("Get data for: ", ticker)
        # Get historical closing price data
        df = stock.history(period="5y") # it doesn't make sense to have ALL the data
        # 5 years is enough (medium term)
        
        # Wait a prudent time
        time.sleep(2) # in seconds
        
        # If there is no data from Yahoo
        if df.empty:
            stocks_not_downloaded.append(ticker)
        
        # Remove a possible period in the file name with a _
        the_file = folder + ticker.replace(".", "_") + '.csv'
        print(the_file, " saved!")
        df.to_csv(the_file)
    except Exception as ex:
        stocks_not_downloaded.append(ticker)
        # err_msg.append(ex)
        print("Could not get data for " + ticker)

# GET DATA IN BATCHES
# batch = 500
folder = PATH + "wilshire_stocks\\"
# for i in range(ntickers):
#     if i % batch != 0:
#         save_to_csv_from_yahoo(folder, tickers[i])
#     else:
#         print("Finished ", i," !!")
#         print("==============================================================")
#         time.sleep(20)
# print("Finished All!")

# print(len(stocks_not_downloaded), " stocks not downloaded.")
# print(stocks_not_downloaded)

# Manual download
save_to_csv_from_yahoo(folder, 'ABB')

# TODO: delete empty files! 
# some times empty files are downloaded, delete them

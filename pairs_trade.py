# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 07:53:17 2017

@author: Jayesh
"""

import time
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pandas.io.data as web
#import zipline as zp
import statsmodels.tsa.stattools as ts
import sys


def create_pairs_dataframe(datadir, symbols):

    #Creates a pandas DataFrame containing the closing price
    #of a pair of symbols based on CSV files containing a datetime
    #stamp and OHLCV data
    
    # Open the individual CSV files and read into pandas DataFrames
    print "Importing CSV data..."
#    sym1 = pd.io.parsers.read_csv(os.path.join(datadir, '%s.csv' % symbols[0]),
 #                                 header=0, index_col=0, 
  #                                names=['Datetime','Open','High','Low','Close','Volume','Adj Close'])
   # sym2 = pd.io.parsers.read_csv(os.path.join(datadir, '%s.csv' % symbols[1]),
    #                              header=0, index_col=0, 
     #                             names=['Datetime','Open','High','Low','Close','Volume','Adj Close'])

    # Fetching Data through Yahoo Finance
    
    sym1 = web.DataReader(symbols[0], data_source='yahoo',start ='2015/6/1',end=time.strftime("%Y/%m/%d"))
    sym2 = web.DataReader(symbols[1], data_source='yahoo',start ='2015/6/1',end=time.strftime("%Y/%m/%d"))
   
  
  #sym1 = web.DataReader(symbols[0], data_source='yahoo',start ='2009/1/1',end='2012/01/01')
    #sym2 = web.DataReader(symbols[1], data_source='yahoo',start ='2009//1',end='2012/01/01')
    
    
    
    print "Constructing dual matrix for %s and %s..." % symbols    
    pairs = pd.DataFrame(index=sym1.index)
    pairs['%s_close' % symbols[0]] = sym1['Adj Close']
    pairs['%s_close' % symbols[1]] = sym2['Adj Close']
    pairs = pairs.dropna()
    
    return pairs

def check_cointegration(pairs, symbols):
    print "Computing Cointegration..."
    #coin_result=ts.coint(pairs['%s_close' % symbols[0].lower()],pairs['%s_close' % symbols[1].lower()] )
    coin_result=ts.coint(pairs['%s_close' % symbols[0]],pairs['%s_close' % symbols[1]] )
    #Confidence Level chosen as 0.05 (5%)
    return coin_result[1]
    
def calculate_spread_zscore(pairs, symbols):
    
           
    
    pairs['returns']=np.log(pairs['%s_close' % symbols[0]]/pairs['%s_close' %symbols[1]])
    pairs['mean']=pairs['returns'].rolling(window=30,center=False).mean()
    #pairs['hedge_ratio'] = model.beta['x']
    pairs = pairs.dropna()
    

    # Create the spread and then a z-score of the spread
    print "Creating the spread/zscore columns..."
    #pairs['spread'] = pairs['spy_close'] - pairs['hedge_ratio']*pairs['iwm_close']
    
     
    pairs['zscore'] = (pairs['returns'] - pairs['mean'])/pairs['returns'].rolling(window=30,center=False).std()
    print "After ??"
#np.std(
       #(pairs['returns']:pairs['returns'].shift(30)).std()
       #pd.NIF
    #pd.rolling_std(pairs['returns'],window=30)
    pairs['returns'].rolling(window=30,center=False).std()
    return pairs    
 

def signal_generate(pairs, symbols, 
                                     z_entry_threshold=2.0, 
                                     z_exit_threshold1=0.5,
                                     z_exit_threshold2=3.5):
    """Create the entry/exit signals based on the exceeding of 
    z_enter_threshold for entering a position and falling below
    z_exit_threshold for exiting a position."""

    # Calculate when to be long, short and when to exit
    pairs['longs'] = (pairs['zscore'] <= -z_entry_threshold)*1.0
    pairs['shorts'] = (pairs['zscore'] >= z_entry_threshold)*1.0
  #  pairs['pos'] = pairs['longs'] - pairs['shorts']
 
#
    pairs['exits'] = ((np.abs(pairs['zscore']) <= z_exit_threshold1 ) )*1.0
#or (np.abs(pairs['zscore']) >= z_exit_threshold2 ) 

     #pairs['zscore']/np.abs(pairs['zscore']) == (pairs['zscore'].shift(1))/(np.abs(pairs['zscore'].shift(1)))
    
    
    
    pairs['long_market'] = 0.0
    pairs['short_market'] = 0.0

    # These variables track whether to be long or short while
    # iterating through the bars
    long_market = 0
    short_market = 0

    # Vectorized Possible ?
        
    print "Calculating when to be in the market (long and short)..."
    for i, b in enumerate(pairs.iterrows()):
        # Calculate longs
        if pairs['longs'][i-1] == 1.0:
            long_market = 1            
        # Calculate shorts
        if pairs['shorts'][i-1] == 1.0:
#b[1]['shorts'] == 1.0:
            short_market = 1
            
            
        # Calculate exits
        #if b[1]['exits'] == 1.0 and  pairs['zscore'][i]/np.abs(pairs['zscore'][i]) ==  (pairs['zscore'][i-1])/(np.abs(pairs['zscore'][i-1])):
        if pairs['exits'][i-1] == 1.0 or  ((np.abs(pairs['zscore'][i]-pairs['zscore'][i-1]) > 1) and (np.abs(pairs['zscore'][i]+pairs['zscore'][i-1]) < 1)) :
                                  
            pairs['exits'][i-1]=1
            long_market = 0
            short_market = 0
           
            
            
        pairs.ix[i]['long_market'] = long_market
        pairs.ix[i]['short_market'] = short_market
    return pairs    
    
def portfolio_returns(pairs, symbols,lot_size):
    """Creates a portfolio pandas DataFrame which keeps track of
    the account equity and ultimately generates an equity curve.
    This can be used to generate drawdown and risk/reward ratios."""
    
    # Convenience variables for symbols
    sym1 = symbols[0]
    sym2 = symbols[1]
    #pairs['ret_%s' % symbols[0]]=pairs['%s_close' %sym1]-pairs['%s_close' %sym1].shift(1)
    #pairs['ret_%s' % symbols[1]]=pairs['%s_close' %sym2]-pairs['%s_close' %sym2].shift(1)
    pairs['ret_%s' % symbols[0]]=100*((pairs['%s_close' %sym1]/pairs['%s_close' %sym1].shift(1))-1)
    pairs['ret_%s' % symbols[1]]=100*((pairs['%s_close' %sym2]/pairs['%s_close' %sym2].shift(1))-1)
    
    # Construct the portfolio object with positions information
    # Note that minuses to keep track of shorts!
    print "Constructing a portfolio..."
    portfolio = pd.DataFrame(index=pairs.index)
    portfolio['positions'] = pairs['long_market'] - pairs['short_market']
    pairs['positions'] = pairs['long_market'] - pairs['short_market']
    
    #pairs[sym1] = pairs['ret_%s' % symbols[0]] * portfolio['positions']*lot_size[0]
    #pairs[sym2] = -1.0*pairs['ret_%s' % symbols[1]] * portfolio['positions']*lot_size[1]

    pairs[sym1] = pairs['ret_%s' % symbols[0]] * portfolio['positions']
    pairs[sym2] = -1.0*pairs['ret_%s' % symbols[1]] * portfolio['positions']

    pairs['total'] = pairs[sym1] + pairs[sym2]
    
    portfolio['total'] = pairs[sym1] + pairs[sym2]

    # Construct a percentage returns stream and eliminate all 
    # of the NaN and -inf/+inf cells
    print "Constructing the equity curve..."
    portfolio['returns'] = portfolio['total'].pct_change()
    #pairs['returns'] = portfolio['total'].pct_change()
    portfolio['returns'].fillna(0.0, inplace=True)
    portfolio['returns'].replace([np.inf, -np.inf], 0.0, inplace=True)
    portfolio['returns'].replace(-1.0, 0.0, inplace=True)
    #pairs['cc'] = 100*pairs['total'].pct_change()
    # Calculate the full equity curve
    #portfolio['returns'] = (portfolio['total'] + 1.0).cumsum()
    
    #portfolio['cum_sum'].plot(grid=True)
    #To Caluclate Future Returns
    #(lot_size[0]*pairs['ret_%s' % symbols[0]]).cumsum().plot(grid=True)
    #(lot_size[1]*pairs['ret_%s' % symbols[1]]).cumsum().plot(grid=True)
    #To Calculate Percentage Returns
    portfolio['cum_sum']=portfolio['total'].cumsum().plot()
    (100*np.log(pairs['%s_close' % symbols[0]]/ pairs['%s_close' % symbols[0]].shift(1))).cumsum().plot()
    (100*np.log(pairs['%s_close' % symbols[1]]/ pairs['%s_close' % symbols[1]].shift(1))).cumsum().plot()
    plt.xlabel("DateTime")
    plt.ylabel("Cumulative Returns in %");
    plt.grid(True)

 
    #pairs.to_csv("H:\Quantexcercises\Practice\op.csv")
    return portfolio


    
datadir="H:\Quantexcercises\Practice"

if __name__ == "__main__":    
    

    datadir = "H:\Quantexcercises\Practice"  # Change this to reflect your data path!
    #symbols = ('ICICI', 'SBI')
 #   symbols = ('SBI', 'ICICI')
    symbols = ('SBIN.NS', 'ICICIBANK.NS')
    #symbols = ('ACC.NS', 'AMBUJACEM.NS')
    lot_size= (2500,400)
    
    returns = []

    
    pairs = create_pairs_dataframe(datadir, symbols)
    coint_check = check_cointegration(pairs, symbols)
    if coint_check < 0.47:
        
    #if pairs == 1:
     #   exit(1)
        
         print "Pairs are Cointegrated"
         print coint_check
         #print coint_check
         pairs = calculate_spread_zscore(pairs, symbols)
         pairs = signal_generate(pairs, symbols, 
                                                z_entry_threshold=2.0, 
                                                z_exit_threshold1=0.5,
                                                z_exit_threshold2=3.5)

         portfolio = portfolio_returns(pairs, symbols,lot_size)
       #  returns.append(portfolio.ix[-1]['returns'])

    

    #plt.plot(portfolio['returns'])
    # plt.show()
         pairs.to_csv("H:\Quantexcercises\Practice\op.csv")
        # sys.exit(0)
     
    else:
         print coint_check
         print "Pairs are not CoIntegrated, Exiting..."
         #sys.exit(0)
    
    #pairs.to_csv("H:\Quantexcercises\Practice\op.csv")


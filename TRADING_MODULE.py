#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ccxt
import json 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import hmac
from requests import Request
import tkinter
from datetime import datetime
import re
import requests


# In[385]:


class coin_trading:
    def __init__(self, exchange_id, apiKey, secretKey, pw=0):
        
        '''
        1) 변수 정리
        
        1-1) exchange_id : 코인거래소 이름
        [id : name]
        [binance : Binance]
        [ftx : FTX]
        [huobi : Huobi]
        [okex : OKEX]
        
        1-2) apiKey , secretKey : 발급받은 본인의 해당 거래소 API KEY
        1-3) exchange : CCXT 모듈 사용 거래소
        1-4) ticket_list : 해당 거래소에서 사용하는 코인 티커 리스트
        
        
        2) 함수 정리
        
        2-1) show_trade_history
        해당 TICKER 의 가장 최근의 체결내역을 프린트 합니다. 방금 주문낸 코인의 체결내역을 확인하는 용도로 사용하는 것이 가능합니다.
        2-2) show_open_order
        해당 TICKER 의 미체결 내역을 프린트 합니다. 
        2-3) get_balance
        
        
        '''
        self.exchange_id = exchange_id
        self.apiKey = apiKey
        self.secretKey = secretKey
        self.pw = pw
        self.exchange_info = {
                            "okex":{
                                    'base' :'USDT',
                                    'order_type' : "balance"
            
                                    },
                            'ftx':{
                                    'base' : "USD",
                                    'order_type' : "amount"
                                    },
                            "binance":{
                                    'base' :'USDT',
                                    'order_type' : "amount"
                                    },
                            "upbit":{
                                    'base' :'KRW',
                                    'order_type' : "balance"
                                    }}
            
        if self.exchange_id == "binance":
            self.exchange = ccxt.binance({'apiKey':apiKey, 'secret':secretKey, 'enableRateLimit':True})
        elif self.exchange_id == "ftx":
            self.exchange = ccxt.ftx({'apiKey':apiKey, 'secret':secretKey, 'enableRateLimit':True})
        elif self.exchange_id == "upbit":
            self.exchange = ccxt.upbit({'apiKey':apiKey, 'secret':secretKey, 'enableRateLimit':True,
                                       'options': {'createMarketBuyOrderRequiresPrice': False}})
        elif self.exchange_id == "huobi":
            self.exchange = ccxt.huobi({'apiKey':apiKey, 'secret':secretKey, 'enableRateLimit':True})
        elif self.exchange_id == "okex":
            self.exchange = ccxt.okex5({'apiKey':apiKey, 'secret':secretKey, 'password': pw, 'enableRateLimit':True,
                                       'options': {'createMarketBuyOrderRequiresPrice': False}})
        else:
            print("SORRY! TRY ANOTHER EXCHANGE!")
        
        self.ticket_list = list(self.exchange.fetch_tickers().keys())
    
    def make_exchange_ticker(self, ticker):
        self.ticker = ticker
        if self.exchange_id == "binance":
            self.ticker = self.ticker + "/USDT"
        elif self.exchange_id == "ftx":
            self.ticker = self.ticker + "/USD"
        elif self.exchange_id == "okex":
            self.ticker = self.ticker + "/USDT"
        elif self.exchange_id == "upbit":
            self.ticker = self.ticker + "/KRW"
        return self.ticker
        
    def show_trade_history(self, ticker):
        '''
        해당 TICKER 의 가장 최근의 체결내역을 프린트합니다.
        방금 주문낸 코인의 체결내역을 확인하는 용도로 사용하는 것이 가능합니다.
        '''
        try: 
            trade_history = self.exchange.fetchMyTrades(self.make_exchange_ticker(ticker))[-1]
            print("[ TRADE--HIST ] "+"[ "+trade_history['datetime']+ " || " + trade_history['symbol'] + " || " + trade_history['side']+ " || " +                   "PRICE($) : " + str(trade_history['price']) + " || " +"AMOUNT : "+str(trade_history['amount']) + " ]")
        except:
            print("[ TRADE--HIST ] NOTHING")
    
    def show_open_order(self, ticker):
        '''
        해당 TICKER 의 미체결 내역을 프린트 합니다. 
        '''
        num = len(self.exchange.fetch_open_orders(self.make_exchange_ticker(ticker)))
        if num == 0:
            print("[ OPEN--ORDER ] NOTHING")
        else:
            for i in range(num):
                open_order = self.exchange.fetch_open_orders(self.make_exchange_ticker(ticker))[i]['info']
                print("[ OPEN--ORDER ] "+"[ " + open_order['createdAt'] + " || " + open_order['market'] + " || " + open_order["side"] + " || " +         "PRICE($) : "+ open_order['price']+ " || " + "AMOUNT : "+ open_order['size']+ " ]")
        
    def get_balance(self):
        get_symbols = list(self.exchange.fetch_balance()['total'].keys())
        balance_free = {}
        balance_used = {}
        balance_total = {}
        print( "[ " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " ] " + "CHECK MY BALANCE")
        
        ### FREE (거래 가능 코인잔고)
        free = self.exchange.fetch_balance()['free']
        free_log = "[ FREE----BAL ]" + " " + "[ "
        for i in get_symbols:
            if free[i] == 0 :
                pass
            else:
                free_log += i + " : " + str(free[i]) + " || "
        
        if len(free_log) < 17 :
            print("[ FREE----BAL ] NOTHING")
        else:  
            free_log = free_log[:-4] + " ]"
            print(free_log)
            
        ### USED (거래 진행중 코인잔고)
        used = self.exchange.fetch_balance()['used']
        used_log = "[ USED----BAL ]" + " " + "[ "
        for i in get_symbols:
            if used[i] == 0 :
                pass
            else:
                used_log += i + " : " + str(used[i]) + " || "
        if used_log == "[ USED----BAL ]" + " " + "[ ":
            print("[ USED----BAL ] NOTHING")
        else:  
            used_log = used_log[:-4] + " ]"
            print(used_log)    
    
        ### TOTAL (FREE + USED)
        total = self.exchange.fetch_balance()['total']
        total_log = "[ TOTAL---BAL ]" + " " + "[ "
        for i in get_symbols:
            if total[i] == 0 :
                pass
            else:
                total_log += i + " : " + str(total[i]) + " || "
        if len(total_log) < 18 :
            print("[ TOTAL---BAL ] NOTHING")
        else:  
            total_log = total_log[:-4] + " ]"
            print(total_log) 
    
    def get_futures_positions(self):
        print( "[ " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " ] " + "CHECK MY FUTURES POSITIONS")
        get_fut_bal = self.exchange.fetch_positions()
        positions_num = len(get_fut_bal)
        fut_log = ""
        for i in range(positions_num):
            if float(get_fut_bal[i]['size']) == 0:
                pass
            else:
                fut_log += get_fut_bal[i]['future'] + " || " + get_fut_bal[i]['side'] + " || ENTRY-PRICE($) : " +                get_fut_bal[i]['entryPrice'] + " || " + "AMOUNT : " + get_fut_bal[i]['size'] + " || " + "MARGIN($) : " + get_fut_bal[i]['collateralUsed']
    
        if fut_log == "":
            print("[ FUTURE-OPEN ] NOTHING")
        else:
            fut_log = "[ FUTURE-OPEN ] " + "[ " + fut_log + " ]"
            print(fut_log)
            
            
    def make_order(self, ticker, ratio, side = "buy", order_type = "market"):
        ### BUY
        if side == "buy" or side == "long":
            free_bal = self.exchange.fetch_balance()['free'][self.exchange_info[self.exchange_id]['base']]*ratio
            coin_last_price = self.exchange.fetch_ticker(self.make_exchange_ticker(ticker))['close']
            trading_amount = free_bal/coin_last_price
            order_choice = {"balance":free_bal, "amount":trading_amount}
            # mkt_order = self.exchange.create_order(self.make_exchange_ticker(ticker), "market", side, order_choice[self.exchange_info[self.exchange_id]['order_type']])
            try:
                if order_type == "market":
                    mkt_order = self.exchange.create_order(self.make_exchange_ticker(ticker), "market", side, order_choice[self.exchange_info[self.exchange_id]['order_type']])
                else:
                    print("error")
                    pass
            except:
                print("ORDER FAIL")
        
        ### SELL
        else:
            free_bal = self.exchange.fetch_balance()['free'][ticker]*ratio
            coin_last_price = self.exchange.fetch_ticker(self.make_exchange_ticker(ticker))['close']
            trading_amount = free_bal
            try:
                if order_type == "market":
                    mkt_order = self.exchange.create_order(self.make_exchange_ticker(ticker), "market", side, trading_amount)
                else: 
                    pass
                self.show_trade_history(ticker)
            except:
                print("ORDER FAIL")

                


# In[362]:


binance_apiKey = ''
binance_secret = ''
ftx_apiKey = ''
ftx_secret = ''
okex_apiKey = ""
okex_secret = ""
okex_pw = ""
huobi_apiKey = ''
huobi_secret = ''
upbit_apikey = ''
upbit_secret =''


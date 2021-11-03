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

apiKey = ""
secret = ""

exchange = ccxt.ftx({'apiKey': apiKey, 'secret': secret, 'enableRateLimit': True})

markets = exchange.fetch_tickers()  # ticker 조회
symbols = list(markets.keys())  # coin ticker list


def show_trade_history(ticker):
    # 해당 ticker의 가장 최근의 체결내역을 프린트 합니다.
    # ticker : 해당 종목티커
    trade_history = exchange.fetchMyTrades(ticker)[0]['info']
    print("[ TRADE--HIST ] " + "[ " + trade_history['time'] + " || " + trade_history['market'] + " || " + trade_history[
        'side'] + " || " + "PRICE($) : " + trade_history['price'] + " || " + \
          "AMOUNT : " + trade_history['size'] + " ]")


def show_trade_ALL_history():
    trade_num = len(exchange.fetchMyTrades())
    trade_history_ALL = exchange.fetchMyTrades()
    for i in range(trade_num):
        trade_history = trade_history_ALL[(trade_num - (i + 1))]['info']
        print("[ TRADE--HIST ] " + "[ " + trade_history['time'] + " || " + trade_history['market'] + " || " +
              trade_history['side'] + " || " + "PRICE($) : " + trade_history['price'] + " || " + "AMOUNT : " +
              trade_history['size'] + " ]")


def show_open_order(ticker):
    # 해당 ticker의 미체결 주문을 출력
    # ticker : 해당 종목티커
    num = len(exchange.fetch_open_orders(ticker))
    for i in range(num):
        open_order = exchange.fetch_open_orders(ticker)[i]['info']
        print("[ OPEN--ORDER ] " + "[ " + open_order['createdAt'] + " || " + open_order['market'] + " || " + open_order[
            "side"] + " || " + "PRICE($) : " + open_order['price'] + " || " + "AMOUNT : " + open_order['size'] + " ]")


def show_open_ALL_order():
    print("[ " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " ] " + "CHECK MY OPEN ORDERS")
    # 해당 ticker의 open order 프린트 합니다
    # ticker : 해당 종목티커
    num = len(exchange.fetch_open_orders())
    open_all_order = exchange.fetch_open_orders()
    for i in range(num):
        open_order = open_all_order[i]['info']
        print("[ OPEN--ORDER ] " + "[ " + open_order['createdAt'] + " || " + open_order['market'] + " || " + open_order[
            "side"] + " || " + \
              "PRICE($) : " + open_order['price'] + " || " + "AMOUNT : " + open_order['size'] + " ]")


def get_balance():
    get_symbols = list(exchange.fetch_balance()['total'].keys())
    balance_free = {}
    balance_used = {}
    balance_total = {}
    print("[ " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " ] " + "CHECK MY BALANCE")

    # FREE (거래 가능 코인잔고)
    free = exchange.fetch_balance()['free']
    free_log = "[ FREE----BAL ]" + " " + "[ "
    for i in get_symbols:
        if free[i] == 0:
            pass
        else:
            # balance_free[i] = free[i]
            free_log += i + " : " + str(free[i]) + " || "
    if len(free_log) < 17:
        print("[ FREE----BAL ] NOTHING")
    else:
        free_log = free_log[:-4] + " ]"
        print(free_log)

    # USED (거래 진행중 코인잔고)
    used = exchange.fetch_balance()['used']
    used_log = "[ USED----BAL ]" + " " + "[ "
    for i in get_symbols:
        if used[i] == 0:
            pass
        else:
            used_log += i + " : " + str(used[i]) + " || "
    if len(used_log) < 17:
        print("[ USED----BAL ] [ NOTHING ]")
    else:
        used_log = used_log[:-4] + " ]"
        print(used_log)

    # TOTAL(= FREE + USED)
    total = exchange.fetch_balance()['total']
    total_log = "[ TOTAL---BAL ]" + " " + "[ "
    for i in get_symbols:
        if total[i] == 0:
            pass
        else:
            total_log += i + " : " + str(total[i]) + " || "
    if len(total_log) < 18:
        print("[ TOTAL---BAL ] NOTHING")
    else:
        total_log = total_log[:-4] + " ]"
        print(total_log)


def get_futures_positions():
    print("[ " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " ] " + "CHECK MY FUTURES POSITIONS")
    get_fut_bal = exchange.fetch_positions()
    positions_num = len(get_fut_bal)
    fut_log = ""
    for i in range(positions_num):
        if float(get_fut_bal[i]['size']) == 0:
            pass
        else:
            fut_log += get_fut_bal[i]['future'] + " || " + get_fut_bal[i]['side'] + " || ENTRY-PRICE($) : " + \
                       get_fut_bal[i]['entryPrice'] + " || " + "AMOUNT : " + get_fut_bal[i][
                           'size'] + " || " + "MARGIN($) : " + get_fut_bal[i]['collateralUsed']
    fut_log = "[ FUTURE-OPEN ] " + "[ " + fut_log + " ]"
    print(fut_log)


def my_trading_info():
    get_balance()
    print(" ")
    get_futures_positions()
    print(" ")
    show_open_ALL_order()
    print(" ")
    print("[ " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " ] " + "CHECK MY TRADING HISTORY")
    show_trade_ALL_history()


if __name__ == '__main__':
    my_trading_info()

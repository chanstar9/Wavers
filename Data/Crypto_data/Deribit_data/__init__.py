# -*- coding: utf-8 -*-
"""
:Author: Chankyu Choi
:Date: 2021. 10. 30
"""

from pymongo import MongoClient
from Data.Crypto_data.Deribit_data.Deribit_API import *
from columns import *


if __name__ == '__main__':
    step = 56
    while True:
        # get all option tickers
        BTC_option_instruments = get_instruments_resp(currency=BTC, kind='option')
        ETH_option_instruments = get_instruments_resp(currency=ETH, kind='option')

        # Entire Order Book for each Crypto(BTC, ETH)
        # To DB(DB에 넣을 Data 준비)
        BTC_order_book = get_order_book_data(instruments=BTC_option_instruments, number='BTC' + str(step))
        ETH_order_book = get_order_book_data(instruments=ETH_option_instruments, number='ETH' + str(step))

        # DB에 넣기
        insert_data_MongoDB(data=BTC_order_book)
        insert_data_MongoDB(data=ETH_order_book)
        print(step)
        step += 1

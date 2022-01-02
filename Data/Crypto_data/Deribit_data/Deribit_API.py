# -*- coding: utf-8 -*-
"""
:Author: Jeonghwa Hong
:Date: 2021. 09. 22
"""

import certifi
import asyncio
import websockets
import json
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
from dateutil.parser import parse
from tqdm import tqdm
from columns import *


async def call_api(msg):
    async with websockets.connect('wss://www.deribit.com/ws/api/v2', ping_interval=None) as websocket:
        await websocket.send(msg)
        while websocket.open:
            response = await websocket.recv()
            return response


def async_loop(api, msg):
    return asyncio.get_event_loop().run_until_complete(api(msg))


def retrieve_historic_data(start, end, instrument, timeframe):
    msg = {
        "jsonrpc": "2.0",
        "id": 833,
        "method": "public/get_tradingview_chart_data",
        "params": {
            "instrument_name": instrument,
            "start_timestamp": start,
            "end_timestamp": end,
            "resolution": timeframe
        }
    }
    resp = async_loop(call_api, json.dumps(msg))

    return resp


## JSON 요청문
def get_instruments_resp(currency, kind):
    msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "public/get_instruments",
        "params": {
            "currency": currency,
            "kind": kind,
            "expired": False
        }
    }
    resp = json.loads(async_loop(call_api, json.dumps(msg)))
    tickers = []
    for instrument in resp['result']:
        tickers.append(instrument[INSTRUMENT_NAME])
    return tickers


def get_index_price_resp(index_name: str):
    """
    This function is designed to get 'response' for option data
    :param instrument_name: Ex) "BTC-1OCT21-44000-P"
    :return: resp has a 'JSON' type value
    """
    msg = \
        {"jsonrpc": "2.0",
         "method": "public/get_index_price",
         "id": 42,
         "params": {
             "index_name": index_name}
         }
    resp = async_loop(call_api, json.dumps(msg))
    return resp


def get_order_book_resp(instrument_name: str):
    """
    This function is designed to get 'response' for option data
    :param instrument_name: Ex) "BTC-1OCT21-44000-P"
    :return: resp has a 'JSON' type value
    """
    msg = {
        "jsonrpc": "2.0",
        "id": 8772,
        "method": "public/get_order_book",
        "params": {
            "instrument_name": instrument_name,
            "depth": 50
        }
    }
    resp = async_loop(call_api, json.dumps(msg))
    return resp


def get_last_trades_by_instrument_resp(instrument_name: str):
    """
    This function is designed to get 'response' for option data
    :param instrument_name: Ex) "BTC-1OCT21-44000-P"
    :return: resp has a 'JSON' type value
    """
    msg = {
        "jsonrpc": "2.0",
        "id": 9267,
        "method": "public/get_last_trades_by_instrument",
        "params": {
            "instrument_name": instrument_name,
            "count": 1
        }
    }
    resp = async_loop(call_api, json.dumps(msg))
    return resp


## JSON 결과 파일 DataFrame 변환
def json_to_dataframe(json_resp, resp: str):
    res = json.loads(json_resp)

    df = 0  ## df is empty
    if resp == 'get_order_book':
        df = pd.DataFrame(res)['result']
        df['timestamp'] = datetime.fromtimestamp(df['timestamp'] / 1000)

    elif resp == 'get_instruments':
        df = res['result']

    if df == 0:
        raise ValueError("There is no such 'resp' value.")

    return df


def check_overlap_NUM(number: str):
    ca = certifi.where()
    cluster = MongoClient(
        'mongodb+srv://admin:chankyu9@cluster0.4urzo.mongodb.net/Crypto?retryWrites=true&w=majority',
        tlsCAFile=ca)

    db = cluster['Crypto']
    Option = db['Option']
    exist = Option.find_one({NUM: number})
    if exist is None:
        print('No overlap.')
        return False
    else:
        print('Overlapped.')
        return True


def get_index_price(index_name: str):
    resp = get_index_price_resp(index_name=index_name)
    btc_spot = json.loads(resp)['result']['index_price']
    return btc_spot


def get_order_book_data(instruments: list, number: str):
    # instruments = BTC_option_instruments

    # Checking the overlap of param number with DB
    check_overlap = check_overlap_NUM(number=number)
    if check_overlap:
        raise ValueError("The number already exists.")

    tick_list = list()
    for name in tqdm(instruments):
        # name=BTC_option_instruments[24]
        order_book_json_resp = get_order_book_resp(instrument_name=name)
        # last_trade_json_resp = get_last_trades_by_instrument_resp(instrument_name=name)

        # Converting JSON format response to dictionary
        ob_dict_resp = json.loads(order_book_json_resp)['result']
        # try:
        #     lt_dict_resp = json.loads(last_trade_json_resp)['result']['trades'][0]
        # except IndexError:  # last_trade가 없는 경우 제외
        #     continue

        date = datetime.fromtimestamp(ob_dict_resp['timestamp'] / 1000)
        tick = {
            ID: str(ob_dict_resp['change_id']) + '_' + str(ob_dict_resp['timestamp']),
            NUM: number,
            TIMESTAMP: ob_dict_resp['timestamp'],
            CALENDAR: {YEAR: date.year, MONTH: date.month, DAY: date.day,
                       HOUR: date.time().hour, MINUTE: date.time().minute},
            NAME: ob_dict_resp['instrument_name'],
            T_VOL: ob_dict_resp['stats']['volume'],
            UNDERLYING: ob_dict_resp['underlying_index'],
            ASK_1A: ob_dict_resp['best_ask_amount'],
            ASK_1P: ob_dict_resp['best_ask_price'],
            BID_1A: ob_dict_resp['best_bid_amount'],
            BID_1P: ob_dict_resp['best_bid_price'],
            OI: ob_dict_resp['open_interest'],
            UNDER_P: ob_dict_resp['index_price'],
            LAST_P: ob_dict_resp['last_price'],
            VOL: ob_dict_resp['mark_iv']
        }

        tick_list.append(tick)

    return tick_list


def split_name_info(name: str):
    """
    :param name: ex)"BTC-1OCT21-44000-P"
    :return: Dictionary with MAT, STRIKE, CP
    """
    info_dict = dict()

    name_list = name.split(sep='-')
    info_dict[MAT] = parse(name_list[1])
    info_dict[STRIKE] = int(name_list[2])
    info_dict[CP] = name_list[-1]

    return info_dict


def add_columns(df):
    '''
    :param df: DataFrame directly from MongoDB
    :return: reformed DataFrame which includes maturity, strike and CP columns extracted from NAME.
    '''
    df[[MAT, STRIKE, CP]] = df.apply(lambda x: split_name_info(name=x[NAME]),
                                     axis=1, result_type='expand')
    df[TTM] = df.apply(lambda x: (x[MAT] -
                                  datetime.fromtimestamp(x[TIMESTAMP] / 1000)).days / 365, axis=1)
    return df


def insert_data_MongoDB(data):
    ca = certifi.where()
    cluster = MongoClient(
        'mongodb+srv://admin:chankyu9@cluster0.4urzo.mongodb.net/Crypto?retryWrites=true&w=majority',
        tlsCAFile=ca)

    db = cluster['Crypto']
    Option = db['Option']
    Option.insert_many(data)


def find_data_MongoDB(number: str):
    number = 'BTC1'
    ca = certifi.where()
    cluster = MongoClient(
        'mongodb+srv://admin:chankyu9@cluster0.4urzo.mongodb.net/Crypto?retryWrites=true&w=majority',
        tlsCAFile=ca)

    db = cluster['Crypto']
    Option = db['Option']

    results = Option.find({NUM: number})
    output = [res for res in results]

    # Spliting NAME info into columns(Maturity, Strike, CP, Time to Maturity)
    df = add_columns(df=pd.DataFrame(output))

    return df


if __name__ == '__main__':
    # start = 1554373800000
    # end = 1554376800000
    instrument = "BTC-1OCT21-44000-P"
    timeframe = '1'

    # json_resp = retrieve_historic_data(start, end, instrument, timeframe)
    # json_resp = get_order_book_resp(instrument)

    # get all option tickers
    BTC_option_instruments = get_instruments_resp(currency=BTC, kind='option')
    ETH_option_instruments = get_instruments_resp(currency=ETH, kind='option')

    # Order_Book 조회
    inst = instrument
    order_book_resp = get_order_book_resp(inst)
    order_book_info = json_to_dataframe(json_resp=order_book_resp, resp='get_order_book')

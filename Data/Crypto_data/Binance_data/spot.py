# -*- coding: utf-8 -*-
"""
:Author: Sehoon Kim
:Date: 2021. 09. 22
"""
import websocket
import json
from Data.Crypto_data.Binance_data.auxiliary_functions import *
from pymongo import MongoClient
import certifi

from columns import *

ca = certifi.where()
cluster = MongoClient(
    'mongodb+srv://admin:chankyu9@cluster0.4urzo.mongodb.net/Crypto?retryWrites=true&w=majority', tlsCAFile=ca)
db = cluster['Crypto']
Spot_DB = db['Spot']


def on_message_spot(ws, message):
    json_message = json.loads(message)
    if 'aggTrade' in json_message['stream']:
        spot_tick = {
            ID: json_message['data']['f'],
            TIMESTAMP: json_message['data']['E'],  # event time
            NAME: (json_message['stream'][:-9]).upper(),
            LAST_P: json_message['data']['p'],
            T_VOL: json_message['data']['q'],
        }
        Spot_DB.insert_one(spot_tick)
        print(spot_tick)
    else:
        spot_tick = {
            ID: json_message['data']['u'],
            TIMESTAMP: json_message['data']['E'],  # event time
            NAME: (json_message['stream'][:-13]).upper(),
            BID_1P: json_message['data']['b'][2][0],
            BID_1A: json_message['data']['b'][2][1],
            BID_2P: json_message['data']['b'][1][0],
            BID_2A: json_message['data']['b'][1][1],
            BID_3P: json_message['data']['b'][0][0],
            BID_3A: json_message['data']['b'][0][1],
            ASK_1P: json_message['data']['a'][2][0],
            ASK_1A: json_message['data']['a'][2][1],
            ASK_2P: json_message['data']['a'][1][0],
            ASK_2A: json_message['data']['a'][1][1],
            ASK_3P: json_message['data']['a'][0][0],
            ASK_3A: json_message['data']['a'][0][1]
        }
        Spot_DB.insert_one(spot_tick)
        print(spot_tick)


def spot_data(coin_ticker_list):
    stream_name = ['aggTrade', 'depth@100ms']
    request_list = ''
    for i in stream_name:
        for j in coin_ticker_list:
            request_list += j.lower() + '@' + i + '/'
    request_list = request_list[:-1]
    spot_socket = f"wss://stream.binance.com:9443/stream?streams=" + request_list
    ws = websocket.WebSocketApp(spot_socket, on_message=on_message_spot, on_close=on_close)
    ws.run_forever()


if __name__ == '__main__':
    spot_data(Binance_ticker_list[:3])

# -*- coding: utf-8 -*-
"""
:Author: Chankyu Choi
:Date: 2021. 09. 22
"""


def on_message(ws, message):
    print(message)


def on_close(ws, close_status_code, close_msg):

    print("### closed ###")

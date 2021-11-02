# -*- coding: utf-8 -*-
"""
:Author: Chankyu Choi
:Date: 2021. 08. 11
"""
import datetime as dt
import matplotlib.pyplot as plt
from columns import *
from bs_formula import *
from Data.Crypto_data.Deribit_data.Deribit_API import find_data_MongoDB


def mkt_gamma_crypto(df, graph=True, title=None):
    # filter

    r, q = (0, 0)
    df = df[df[TTM] > 15 / 365]
    df = df[df[VOL] > 0.001]
    df.dropna(subset=[OI], inplace=True)
    df['gamma'] = df.apply(lambda x: bs_gamma(x[UNDER_P], x[STRIKE], x[TTM], r, q, x[VOL], 1), axis=1)
    df['gamma'] = df.apply(lambda x: x['gamma'] * x[OI] if x[CP] == 'C' else -x['gamma'] * x[OI],
                           axis=1)

    df['group'] = df.apply(
        lambda x: int(x[STRIKE] / (10 ** (len(str(int(x[STRIKE]))) - 3))) * (
                10 ** (len(str(int(x[STRIKE]))) - 3)), axis=1)
    df = df.groupby('group')['gamma'].sum()

    if graph:
        x = np.arange(len(df))
        plt.bar(x, df.values)
        plt.xticks(x, df.index, rotation=90)
        plt.title(title)
        plt.show()
    return df


def mkt_vanna_crypto(df, graph=True, title=None):
    # filter
    # df = btc_df
    r, q = (0, 0)
    # df = df[df[TTM] > 15 / 365]
    df = df[df[VOL] > 0.001]
    df.dropna(subset=[OI], inplace=True)

    df['vanna'] = df.apply(lambda x: bs_vanna(x[UNDER_P], x[STRIKE], x[TTM], r, q, x[VOL], 1), axis=1)

    df['vanna'] = df.apply(lambda x: x['vanna'] * x[OI] if x[CP] == 'C' else -x['vanna'] * x[OI], axis=1)
    df['group'] = df.apply(
        lambda x: int(x[STRIKE] / (10 ** (len(str(int(x[STRIKE]))) - 3))) * (
                10 ** (len(str(int(x[STRIKE]))) - 3)), axis=1)
    df = df.groupby('group')['vanna'].sum()

    if graph:
        x = np.arange(len(df))
        plt.bar(x, df.values)
        plt.xticks(x, df.index, rotation=90)
        plt.title(title)
        plt.show()
    return df


if __name__ == '__main__':
    # From DB(DB에서 가져온 후 전처리할 데이터: BTC_order_book)
    btc_df = find_data_MongoDB(number='BTC1')
    eth_df = find_data_MongoDB(number='ETH1')

    # 가져온 데이터에 대한 Mkt_gamma
    BTC_gammas = mkt_gamma_crypto(btc_df, graph=True, title='BTC mkt gamma(spot: {})'.format(543100))
    ETH_gammas = mkt_gamma_crypto(eth_df, graph=True, title='ETH mkt gamma(spot: {})'.format(3440))

    # 가져온 데이터에 대한 Mkt_vanna
    BTC_vannas = mkt_vanna_crypto(btc_df, graph=True, title='BTC mkt vanna(spot: {})'.format(543100))

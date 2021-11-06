# -*- coding: utf-8 -*-
"""
:Author: Chankyu Choi
:Date: 2021. 08. 11
"""
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
from columns import *
from bs_formula import *
from Data.Crypto_data.Deribit_data.Deribit_API import find_data_MongoDB


def arrange_x(x, number_cut):
    digit = len(str(int(x)))
    result = int(x / (10 ** (digit - number_cut))) * (10 ** (digit - number_cut))
    return result

def mkt_gamma_crypto(df, graph=True, title=None, number_cut=3):
    # filter

    r, q = (0, 0)
    #df = df[df[TTM] > 15 / 365]
    #df = df[df[VOL] > 0.001]
    df.dropna(subset=[OI], inplace=True)
    df['gamma'] = df.apply(lambda x: bs_gamma(x[UNDER_P], x[STRIKE], x[TTM], r, q, x[VOL], 1), axis=1)
    df['gamma'] = df.apply(lambda x: x['gamma'] * x[OI] if x[CP] == 'C' else -x['gamma'] * x[OI],
                           axis=1)

    df['group'] = df.apply(lambda x: arrange_x(x=x[STRIKE], number_cut=number_cut), axis=1)
    df = df.groupby('group')['gamma'].sum()

    if graph:
        x = np.arange(len(df))
        plt.bar(x, df.values)
        plt.xticks(x, df.index, rotation=90)
        plt.title(title)
        plt.show()
    return df


def mkt_vanna_crypto(df, graph=True, title=None, x_axis=VOL):
    # filter
    df = btc_df
    r, q = (0, 0)
    # df = df[df[TTM] > 15 / 365]
    df = df[df[VOL] > 0.001]
    df.dropna(subset=[OI], inplace=True)

    df['vanna'] = df.apply(lambda x: bs_vanna(x[UNDER_P], x[STRIKE], x[TTM], r, q, x[VOL], 1), axis=1)

    df['vanna'] = df.apply(lambda x: x['vanna'] * x[OI] if x[CP] == 'C' else -x['vanna'] * x[OI], axis=1)
    df.dropna(subset=['vanna'], inplace=True)

    if x_axis == STRIKE:
        number_cut = 3
    else:
        number_cut = 2

    df['group'] = df.apply(lambda x: arrange_x(x=x[x_axis], number_cut=number_cut), axis=1)
    df = df.groupby('group')['vanna'].sum()

    if graph:
        x = np.arange(len(df))
        plt.bar(x, df.values)
        plt.xticks(x, df.index, rotation=90)
        plt.title(title)
        plt.show()
    return df

def heatmap_maker(df):
    df_vannas = mkt_vanna_crypto(df, graph=False)
    df_gammas = mkt_gamma_crypto(df, graph=False)

    vannas = df_vannas.to_numpy()
    gammas = df_vannas.to_numpy()
    GEX_grid = np.zeros((len(vannas), len(gammas)))
    for i, v in enumerate(vannas):
        for j, g in enumerate(gammas):
            GEX_grid[i, j] = v + g

    # HeatMap
    plt.rcParams['figure.figsize'] = [10, 8]
    plt.pcolor(GEX_grid)
    plt.xticks(np.arange(0.5, GEX_grid.shape[0], 1), df_vannas.index)
    plt.yticks(np.arange(0.5, GEX_grid.shape[1], 1), df_gammas.index)
    plt.title('Heatmap', fontsize=20)
    plt.xlabel('VOL', fontsize=14)
    plt.ylabel('price', fontsize=14)
    plt.colorbar()
    plt.show()

def Discrete_QV(x):
    r = np.log(1.027)
    dK = 2.5
    tau = x['TTM'] / 252
    B = np.exp(-r * tau)
    sums = (x['Close'] * dK) / (B *(x['Strike'] ** 2))
    res = (2 / tau) * sums
    return res.sum()

if __name__ == '__main__':
    # From DB(DB에서 가져온 후 전처리할 데이터: BTC_order_book)
    btc_df = find_data_MongoDB(number='BTC200')
    eth_df = find_data_MongoDB(number='ETH1')


    # 가져온 데이터에 대한 Mkt_gamma
    BTC_gammas = mkt_gamma_crypto(btc_df, graph=True, title='BTC mkt gamma(spot: {})'.format(543100))
    ETH_gammas = mkt_gamma_crypto(eth_df, graph=True, title='ETH mkt gamma(spot: {})'.format(3440))


    # 가져온 데이터에 대한 Mkt_vanna
    BTC_vannas = mkt_vanna_crypto(df=btc_df,
                                  x_axis=VOL,
                                  title='BTC mkt vanna(spot: {})'.format(0))
    #GEX+
    heatmap_maker(df=btc_df)

# -*- coding: utf-8 -*-
"""
:Author: Chankyu Choi
:Date: 2021. 08. 11
"""
from tqdm import tqdm
import datetime as dt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from columns import *
from bs_formula import *
from Data.Crypto_data.Deribit_data.Deribit_API import find_data_MongoDB


def arrange_x(x, number_cut):
    digit = len(str(int(x)))
    result = int(x / (10 ** (digit - number_cut))) * (10 ** (digit - number_cut))
    return result


def gamma_by_strikes(df, graph=True, title=None, number_cut=3):
    r, q = (0, 0)

    # filter
    df = df[df[TTM] > 10 / 365]
    df = df[df[VOL] > 0.001]
    df.dropna(subset=[OI], inplace=True)
    df[GAMMA] = df.apply(lambda x: bs_gamma(x[UNDER_P], x[STRIKE], x[TTM], r, q, x[VOL], 1), axis=1)
    df[GAMMA] = df.apply(lambda x: x[GAMMA] * x[OI] if x[CP] == 'C' else -x[GAMMA] * x[OI], axis=1)

    df['group'] = df.apply(lambda x: arrange_x(x=x[STRIKE], number_cut=number_cut), axis=1)
    df = df.groupby('group')[GAMMA].sum()

    if graph:
        x = np.arange(len(df))
        plt.bar(x, df.values)
        plt.xticks(x, df.index, rotation=90)
        plt.title(title)
        plt.show()
    return df


def mkt_greeks(df, spot, vol, greeks):
    r, q = (0, 0)

    # filter
    df = df[df[TTM] > 7 / 365]  # except daily and weekly option
    df = df[df[VOL] > 0.001]
    df.dropna(subset=[OI], inplace=True)
    if greeks == GAMMA:
        df[GAMMA] = df.apply(lambda x: bs_gamma(spot, x[STRIKE], x[TTM], r, q, vol, 1), axis=1)
        df[GAMMA] = df.apply(lambda x: x[GAMMA] * x[OI] if x[CP] == 'C' else -x[GAMMA] * x[OI], axis=1)
        return df[GAMMA].sum() * spot
    if greeks == VANNA:
        df[VANNA] = df.apply(lambda x: bs_vanna(spot, x[STRIKE], x[TTM], r, q, vol, 1), axis=1)
        df[VANNA] = df.apply(lambda x: x[VANNA] * x[OI] if x[CP] == 'C' else -x[VANNA] * x[OI], axis=1)
        return df[VANNA].sum() * spot


def heatmap_maker(df, spot, vol):
    spot_lst = np.round(spot * np.arange(0.8, 1.15, 0.01))
    vol_lst = np.round(vol * np.arange(0.7, 1.3, 0.01))

    GEX_grid = np.zeros((len(spot_lst), len(vol_lst)))
    VEX_grid = np.zeros((len(spot_lst), len(vol_lst)))
    for i, _spot in tqdm(enumerate(spot_lst)):
        for j, _vol in enumerate(vol_lst):
            GEX_grid[i, j] = mkt_greeks(df, _spot, _vol / 100, greeks=GAMMA)
            VEX_grid[i, j] = mkt_greeks(df, _spot, _vol / 100, greeks=VANNA)

    total_grid = GEX_grid + VEX_grid
    total_grid = pd.DataFrame(total_grid, index=spot_lst, columns=vol_lst)

    # HeatMap
    ax = sns.heatmap(total_grid, cbar=True, cmap='Blues')
    ax.set_title("GEX+ map, spot: {}, vol: {}".format(spot, vol))
    ax.set_xlabel("Implied Volatility")
    ax.set_ylabel("Spot")
    ax.axvline("")
    plt.show()


if __name__ == '__main__':
    # From DB(DB에서 가져온 후 전처리할 데이터: BTC_order_book)
    num = 1
    btc_df = find_data_MongoDB(number='BTC{}'.format(num))
    eth_df = find_data_MongoDB(number='ETH{}'.format(num))

    # 가져온 데이터에 대한 Mkt_gamma
    BTC_gammas = gamma_by_strikes(btc_df, graph=True, title='BTC mkt gamma(num: {})'.format(num), number_cut=3)
    ETH_gammas = gamma_by_strikes(eth_df, graph=True, title='ETH mkt gamma(num: {})'.format(num), number_cut=2)

    # GEX+
    btc_df.dropna(subset=[OI], inplace=True)
    btc_df = btc_df[btc_df[TTM] > 7 / 365]  # except daily and weekly option
    btc_df = btc_df[btc_df[VOL] > 0.001]
    heatmap_maker(df=btc_df, spot=btc_df[UNDER_P].mean(), vol=btc_df[VOL].mean())

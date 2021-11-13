import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from columns import *
from scipy.interpolate import CubicSpline
from Data.Crypto_data.Deribit_data.Deribit_API import find_data_MongoDB


def ATM_vol_term(df: pd.DataFrame, currency='BTC', tolerance=0.09):
    df[MONEYNESS] = df.apply(lambda x: np.log(x[UNDER_P] / x[STRIKE]), axis=1)
    df.sort_values(by=[MONEYNESS, TTM], inplace=True)  # 0.01
    df_ATM = df[abs(df[MONEYNESS]) <= tolerance].sort_values(by=[TTM]).groupby(by=[TTM]).mean()

    x = df_ATM.index
    cx = CubicSpline(x=x, y=df_ATM[VOL])
    plt.plot(x, cx(x))
    plt.savefig('Image_greeks/{}_ATM_TERMSTRUCTURE'.format(currency))
    plt.close()
    return df_ATM[VOL]


if __name__ == '__main__':
    # From DB(DB에서 가져온 후 전처리할 데이터: BTC_order_book)
    btc_df = find_data_MongoDB(number='BTC1')
    eth_df = find_data_MongoDB(number='ETH1')

    # ATM_vol_termstructure
    ATM_vol_term = ATM_vol_term(df=btc_df)

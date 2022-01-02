import sys
import numpy as np
import pandas as pd
import ccxtpro
import asyncio

from columns import *


def NAV(price: float, coin=BTC, token_style='BULL'):
    # TOKEN BASKET = (# of PERP, USD)
    if token_style == 'BULL':
        if coin == BTC:
            basket = (0.3544117, -11976.46)
        elif coin == ETH:
            basket = (0.8349128, -2242.908)
        elif coin == MATIC:
            basket = (0.6055604, -1.097788)
    elif token_style == 'BEAR':
        if coin == BTC:
            basket = (-0.000000007326749, 0.0004660878)
    NAV = basket[0] * price + basket[1]
    return NAV


def ftx_pair(ftx_symbol: list, token_style='BULL'):
    tickers = []
    for symbol in ftx_symbol:
        futures, token = symbol + '-' + PERP, symbol + token_style + '/' + USD
        if symbol == BTC:
            token_btc = token[3:]
            pair = (futures, token_btc)
            tickers.append(pair)
        else:
            pair = (futures, token)
            tickers.append(pair)
    return tickers


def weighted_averg_price(data, num=3):
    price, vol = [np.array(data[:num])[:, i] for i in range(2)]
    vol_weight = vol / vol.sum()
    wap = (price * vol_weight).sum()
    return wap


async def main():
    exchange = ccxtpro.ftx()
    await exchange.watch_ticker('BULL/USD')
    token_style, num_price = 'BULL', 1
    exclude_lst = [BNB, SOL, XRP, AVAX, LUNA, ADA]
    ftx_symbols = [symbol for symbol in coin_symbol_list if symbol not in exclude_lst]
    ftx_pairs = ftx_pair(ftx_symbol=ftx_symbols, token_style=token_style)
    ftx_tickers = sum([list(pair) for pair in ftx_pairs], [])

    while True:
        orderbooks = await asyncio.gather(exchange.watch_order_book(ftx_pairs[0][0]),
                                          # exchange.watch_ticker(FTX_total_symbol_list[0]),
                                          exchange.watch_order_book(ftx_pairs[0][1]),
                                          exchange.watch_order_book(ftx_pairs[1][0]),
                                          # exchange.watch_ticker(FTX_total_symbol_list[2]),
                                          exchange.watch_order_book(ftx_pairs[1][1]),
                                          exchange.watch_order_book(ftx_pairs[2][0]),
                                          # exchange.watch_ticker(FTX_total_symbol_list[4]),
                                          exchange.watch_order_book(ftx_pairs[2][1])
                                          )
        # futures_close = [orderbooks[i]['close'] for i in range(len(orderbooks)) if (i-1)%3 == 0]
        # orderbooks = [orderbooks[i] for i in range(len(orderbooks)) if (i-1)%3 != 0]

        # close_lst = dict(zip(FTX_coin_symbol_list, futures_close))
        order_lst = dict(zip(ftx_tickers, orderbooks))
        for pair, symbol in zip(ftx_pairs, ftx_symbols):
            # pair, symbol = list(zip(ftx_pairs, ftx_symbols))[0]
            futures, token = pair

            # close = close_lst[symbol]

            # Weighted Average Price
            futures_bids_wap, futures_asks_wap = weighted_averg_price(data=order_lst[futures]['bids'],
                                                                      num=num_price), \
                                                 weighted_averg_price(data=order_lst[futures]['asks'],
                                                                      num=num_price)
            token_bids_wap, token_asks_wap = weighted_averg_price(data=order_lst[token]['bids'],
                                                                  num=num_price), \
                                             weighted_averg_price(data=order_lst[token]['asks'],
                                                                  num=num_price)
            nav_long, nav_short = NAV(price=futures_bids_wap,
                                      coin=symbol,
                                      token_style=token_style), \
                                  NAV(price=futures_asks_wap,
                                      coin=symbol,
                                      token_style=token_style)
            long_spread, long_spread_ratio = token_bids_wap - nav_short, (token_bids_wap / nav_short - 1) * 100
            short_spread, short_spread_ratio = token_asks_wap - nav_long, (token_asks_wap / nav_long - 1) * 100

            profit, profit_ratio = short_spread - long_spread, short_spread_ratio - long_spread_ratio

            # if profit >= 0:
            print(symbol)
            print("NAV(매수/매도): ", round(nav_long, 2), round(nav_short, 2))
            print("선물호가(매수/매도):", round(futures_bids_wap, 2), round(futures_asks_wap, 2))
            print("토큰호가(매수/매도):", round(token_bids_wap, 2), round(token_asks_wap, 2))
            print("{} 매수 스프레드: {} ({}%)".format(symbol, round(long_spread, 4), round(long_spread_ratio, 3)))
            print("{} 매도 스프레드: {} ({}%)".format(symbol, round(short_spread, 4), round(short_spread_ratio, 3)))
            print("{} 차익거래유인: {} ({}%)".format(symbol, round(profit, 4), round(profit_ratio, 4)))
            print("      ")


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.get_event_loop().run_until_complete(main())

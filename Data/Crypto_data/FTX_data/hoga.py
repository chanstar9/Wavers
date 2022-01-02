import sys
import ccxtpro
import asyncio

from columns import *


async def main():
    exchange = ccxtpro.ftx()
    FTX_coin_symbol_list = [symbol for symbol in coin_symbol_list if symbol not in [LUNA, ADA]]
    FTX_total_symbol_list = []
    for symbol in FTX_coin_symbol_list:
        FTX_total_symbol_list.append(symbol + '/' + USD)
        FTX_total_symbol_list.append(symbol + '-' + PERP)

    while True:
        orderbooks = await asyncio.gather(exchange.watch_order_book(FTX_total_symbol_list[0]),
                                          exchange.watch_order_book(FTX_total_symbol_list[1]),
                                          exchange.watch_order_book(FTX_total_symbol_list[2]),
                                          exchange.watch_order_book(FTX_total_symbol_list[3]),
                                          exchange.watch_order_book(FTX_total_symbol_list[4]),
                                          exchange.watch_order_book(FTX_total_symbol_list[5]),
                                          exchange.watch_order_book(FTX_total_symbol_list[6]),
                                          exchange.watch_order_book(FTX_total_symbol_list[7]),
                                          exchange.watch_order_book(FTX_total_symbol_list[8]),
                                          exchange.watch_order_book(FTX_total_symbol_list[9]),
                                          exchange.watch_order_book(FTX_total_symbol_list[10]),
                                          exchange.watch_order_book(FTX_total_symbol_list[11]))

        _lst = dict(zip(FTX_total_symbol_list, orderbooks))
        for symbol in FTX_coin_symbol_list:
            print(symbol)
            print(_lst[symbol + '/' + USD]['asks'][0], _lst[symbol + '/' + USD]['bids'][0])
            print(_lst[symbol + '-' + PERP]['asks'][0], _lst[symbol + '-' + PERP]['bids'][0])
            print("{} 매수차: {}%".format(symbol,
                                       (_lst[symbol + '-' + PERP]['bids'][0][0] / _lst[symbol + '/' + USD]['asks'][0][
                                           0] - 1) * 100))
            print("{} 매도차: {}%".format(symbol,
                                       (_lst[symbol + '/' + USD]['bids'][0][0] / _lst[symbol + '-' + PERP]['asks'][0][
                                           0] - 1) * 100))


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.get_event_loop().run_until_complete(main())

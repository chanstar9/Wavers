import sys
import ccxtpro
import asyncio

import numpy as np
from columns import *


async def main():
    spot_exchange = ccxtpro.binance()
    LAYER1 = [SOL, LUNA, AVAX, FTM, ONE, NEAR]
    NFT = [SAND, MANA, GALA]
    ETH20 = [MATIC, LRC]

    while True:
        orderbooks = await asyncio.gather(spot_exchange.watch_order_book(LAYER1[0] + USDT),
                                          spot_exchange.watch_order_book(LAYER1[1] + USDT),
                                          spot_exchange.watch_order_book(LAYER1[2] + USDT),
                                          spot_exchange.watch_order_book(LAYER1[3] + USDT),
                                          spot_exchange.watch_order_book(LAYER1[4] + USDT),
                                          spot_exchange.watch_order_book(LAYER1[5] + USDT),
                                          spot_exchange.watch_order_book(NFT[0] + USDT),
                                          spot_exchange.watch_order_book(NFT[1] + USDT),
                                          spot_exchange.watch_order_book(NFT[2] + USDT),
                                          spot_exchange.watch_order_book(ETH20[0] + USDT),
                                          spot_exchange.watch_order_book(ETH20[1] + USDT),
                                          )

        _lst = dict(zip(LAYER1 + NFT + ETH20, orderbooks))

        LAYER1_total = 0
        for symbol in LAYER1:
            print(symbol)
            ask_arr = np.array(_lst[symbol]['asks'])
            bid_arr = np.array(_lst[symbol]['bids'])
            symbol_total = (ask_arr[:, 0] * ask_arr[:, 1] + bid_arr[:, 0] * bid_arr[:, 1]).sum()
            print(symbol_total)
            LAYER1_total += symbol_total
        print('LAYER1', LAYER1_total)
        print('=================================')

        NFT_total = 0
        for symbol in NFT:
            print(symbol)
            ask_arr = np.array(_lst[symbol]['asks'])
            bid_arr = np.array(_lst[symbol]['bids'])
            symbol_total = (ask_arr[:, 0] * ask_arr[:, 1] + bid_arr[:, 0] * bid_arr[:, 1]).sum()
            print(symbol_total)
            NFT_total += symbol_total
        print('NFT', NFT_total)
        print('=================================')

        ETH20_total = 0
        for symbol in ETH20:
            print(symbol)
            ask_arr = np.array(_lst[symbol]['asks'])
            bid_arr = np.array(_lst[symbol]['bids'])
            symbol_total = (ask_arr[:, 0] * ask_arr[:, 1] + bid_arr[:, 0] * bid_arr[:, 1]).sum()
            print(symbol_total)
            ETH20_total += symbol_total
        print('ETH20', ETH20_total)
        print('=================================')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

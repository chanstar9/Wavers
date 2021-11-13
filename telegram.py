from Crypto.Deribit.ImpliedOrderBook import *
from Data.Crypto_data.Deribit_data.Deribit_API import *
from Crypto.Deribit.ATM_vol_term import *
from columns import *


def telegram_greeks(number: str, greek: str, folder_name='Image_greeks'):
    '''

    :param number: ex) 'BTC236'
    :param greek: ex) 'gamma'
    :param folder_name: you need to set a storage folder
    under working directory for saving png files ex) 'Image_geeks'
    '''
    loc_image = '{2}/{0}_{1}.png'.format(number, greek, folder_name)

    import telegram
    telegram_token = "add your token"
    telegram_chat_id = 000000000
    bot = telegram.Bot(token=telegram_token)
    bot.send_photo(chat_id=telegram_chat_id, photo=open(loc_image, 'rb'))

def inner_loop_telegram(df, number, greek=GAMMA, spot_name=None):
    # df = btc_df
    # spot_name = 'btc_usd'
    # number = 'BTC500'
    if greek == GAMMA:
        spot = get_index_price(index_name=spot_name)
        vol = ATM_vol_term(df=df).mean()
        gamma_strike = gamma_by_strikes(df=df, number=number, graph=True, title='{0} gamma_by_strikes(spot: {1})'.format(number[:3], spot), number_cut=3)
        GEX_ = GEX(df=df, spot=spot, vol=vol, number=number, graph=True, title='{0} GEX(spot: {1})'.format(number[:3], spot))
        telegram_greeks(number=number, greek=greek)
        telegram_greeks(number=number, greek='GEX')
    elif greek == VANNA:
        spot = get_index_price(index_name=spot_name)
        vol = ATM_vol_term(df=df).mean()
        VEX_ = VEX(df=df, spot=spot, vol=vol, number=number, graph=True, title='{0} VEX(atm_vol: {1})'.format(number[:3], vol))
        telegram_greeks(number=number, greek='VEX')

def loop_infinite(step=500):

    while True:
        # get all option tickers
        BTC_option_instruments = get_instruments_resp(currency=BTC, kind='option')
        ETH_option_instruments = get_instruments_resp(currency=ETH, kind='option')

        # Entire Order Book for each Crypto(BTC, ETH)
        btc_num, eth_num = ('BTC{}'.format(step), 'ETH{}'.format(step))
        BTC_order_book = get_order_book_data(instruments=BTC_option_instruments, number=btc_num)
        ETH_order_book = get_order_book_data(instruments=ETH_option_instruments, number=eth_num)

        # Telegram 전송(add_columns은 필수 전처리 함수. 자세한 건 함수 설명 참조)
        btc_df = add_columns(df=pd.DataFrame(BTC_order_book))
        eth_df = add_columns(df=pd.DataFrame(ETH_order_book))

        inner_loop_telegram(df=btc_df, number=btc_num, greek=GAMMA, spot_name='btc_usd')
        inner_loop_telegram(df=btc_df, number=btc_num, greek=VANNA, spot_name='btc_usd')
        inner_loop_telegram(df=eth_df, number=eth_num, greek=GAMMA, spot_name='eth_usd')
        inner_loop_telegram(df=eth_df, number=eth_num, greek=VANNA, spot_name='eth_usd')
        print(step)
        step += 1

if __name__ == '__main__':
    loop_infinite(step=501)

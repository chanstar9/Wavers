from pymongo import MongoClient
from Data.Crypto_data.Deribit_data.Deribit_API import *
from Crypto.Deribit.ImpliedOrderBook import *
from Crypto.Deribit.ATM_vol_term import *
import certifi
from columns import *

# reference
# https://docs.mongodb.com/manual/core/document/

ca = certifi.where()
cluster = MongoClient(
    'mongodb+srv://admin:chankyu9@cluster0.4urzo.mongodb.net/Crypto_data?retryWrites=true&w=majority',
    tlsCAFile=ca)

db = cluster['Crypto']
Option = db['Option']

# inserting
option_tick = {
    ID: 0,
    TIMESTAMP: 1607443058651,
    NAME: 'BTC-1OCT21-43000-C',
    LAST_P: 0.015,
    T_VOL: 1.3,
    UNDER_P: 41984.17,
    OI: 60.1,
    ASK_1A: 10,
    ASK_1P: 0.016,
    BID_1A: 0.014,
    BID_1P: 15,
}

Option.insert_one(option_tick)
Option.insert_many([option_tick, option_tick, option_tick])

# finding
all_results = Option.find({})  # find everything

results = Option.find({NAME: 'BTC-1OCT21-48000-C'})
for result in all_results:
    print(result[LAST_P])

# deleting
Option.delete_one({ID: 0})
Option.delete_all()
Option.remove({})

# update
Option.update_one({ID: 0}, {"$set": {NAME: 'BTC-1OCT21-48000-P'}})
Option.update_one({ID: 0}, {"$set": {CP: 2}})

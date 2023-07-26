import MetaTrader5 as mt
import pandas as pd
from mt5 import Meta5
from datetime import datetime
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ", mt.__author__)
print("MetaTrader5 package version: ", mt.__version__)

# login credentials
login = 81051204
password = "Javascript17"
server = "Exness-MT5Trial10"
path = "C:/Program Files/MetaTrader 5/terminal64.exe"


# establish connection to the MetaTrader 5 terminal
if not mt.initialize(path, login=login, password=password, server=server):
    print("initialize() failed, error code =", mt.last_error())
    quit()

# starts the platform with initalize()
mt.initialize(path, login=login, password=password, server=server)

# login to trade account with login()
mt.login(login=login, password=password, server=server)

# get the account info
# account_info = mt.account_info()
#
# if not account_info:
#     print("account info failed, error code =", mt.last_error())
# else:
#     # display trading account data in the form of a list
#     print("Show account_info()._asdict():")
#     account_info_dict = mt.account_info()._asdict()
#     # print(account_info_dict)
#     for prop in account_info_dict:
#         print("  {}={}".format(prop, account_info_dict[prop]))
#     # convert the dictionary into DataFrame and print
#     df = pd.DataFrame(list(account_info_dict.items()), columns=['property', 'value'])
#     print("account_info() as dataframe:")
#     print(df)
#     print(account_info)
#
#
meta = Meta5()

# date_from = (2021, 6, 2)
# date_to = (2023, 4, 5)
# k = mt.history_deals_get(date_from=date_from, date_to=date_to)
# print(k)
# print("end")
# p = meta.history_get_symbol(past_date=date_from, to_date=date_to, symbol="*gbpusdz*")
# print(p)

k = meta.order_send(symbol="AUDUSDz")


# k = mt.orders_total()
# print(k)
#
# meta = Meta5()
# meta.symbol_info(symbol="BTCAUDz")
# meta.order_get_symbol("BTCAUDz")
# meta.order_check(symbol="BTCAUDz")


# order send
# meta5_instance.order_send(symbol="BTCAUDz")

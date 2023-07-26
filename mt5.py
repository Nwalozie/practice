import MetaTrader5 as mt
from datetime import datetime
import pandas as pd
import time
pd.set_option('display.max_columns', 500) # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display


class Meta5:

    def _is_valid_date_tuple(self, date_tuple):
        return isinstance(date_tuple, tuple) and len(date_tuple) == 3

    def history_get_symbol(self, past_date, to_date, symbol):
        if not self._is_valid_date_tuple(past_date) or not self._is_valid_date_tuple(to_date):
            raise ValueError("Invalid date format. Please provide valid tuples (year, month, day).")
        # get the number of deals in history
        from_date = datetime(*past_date)
        to_date = datetime(*to_date)

        # get deals for symbols whose names contain "GBP" within a specified interval
        deals = mt.history_deals_get(from_date, to_date, group=f"*{symbol}*")
        if deals == None:
            print("No deals with group=\"*USD*\", error code={}".format(mt.last_error()))
        elif len(deals) > 0:
            print("history_deals_get({}, {}, group=\"*GBP*\")={}".format(from_date, to_date, len(deals)))

    def history_get_2symbol(self, from_date, to_date, symbol_1, symbol_2):
        # get deals for symbols whose names contain neither "EUR" nor "GBP"
        deals = mt.history_deals_get(from_date, to_date, group="*,!*EUR*,!*GBP*")
        if deals == None:
            print("No deals, error code={}".format(mt.last_error()))
        elif len(deals) > 0:
            print("history_deals_get(from_date, to_date, group=\"*,!*EUR*,!*GBP*\") =", len(deals))
            # display all obtained deals 'as is'
            for deal in deals:
                print("  ", deal)
            print()
            # display these deals as a table using pandas.DataFrame
            df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())
            df['time'] = pd.to_datetime(df['time'], unit='s')
            print(df)

        print("")

    def history_get_symbol_id(self, position_id):
        # get all deals related to the position_id
        position_deals = mt.history_deals_get(position=position_id)
        if position_deals == None:
            print("No deals with position #{}".format(position_id))
            print("error code =", mt.last_error())
        elif len(position_deals) > 0:
            print("Deals with position id #{}: {}".format(position_id, len(position_deals)))
            # display these deals as a table using pandas.DataFrame
            df = pd.DataFrame(list(position_deals), columns=position_deals[0]._asdict().keys())
            df['time'] = pd.to_datetime(df['time'], unit='s')
            print(df)

    def symbols_get_all(self):
        # get all symbols
        symbols = mt.symbols_get()
        print('Symbols: ', len(symbols))

    def symbols_get(self, symbol):
        # get symbols containing RU in their names
        ru_symbols = mt.symbols_get(f"*{symbol}*")
        print(f'len(*{symbol}*): ', len(ru_symbols))
        for s in ru_symbols:
            print(s.name)
        print()

    # def symbols_exclude(self, *args):
    #     # get symbols whose names do not contain USD, EUR, JPY and GBP
    #     group_symbols = mt.symbols_get(group="*,!*USD*,!*EUR*,!*JPY*,!*GBP*")
    #     print('len(*,!*USD*,!*EUR*,!*JPY*,!*GBP*):', len(group_symbols))
    #     for s in group_symbols:
    #         print(s.name, ":", s)

    def symbol_info(self, symbol):
        # attempt to enable the display of the symbol in MarketWatch
        selected = mt.symbol_select(f"{symbol}", True)
        if not selected:
            print(f"Failed to select {symbol}")
            mt.shutdown()
            quit()

        # display symbol properties
        symbol_info = mt.symbol_info(f"{symbol}")
        if symbol_info != None:
            # display the terminal data 'as is'
            print(symbol_info)
            print(f"{symbol}: spread =", symbol_info.spread, "  digits =", symbol_info.digits)
            # display symbol properties as a list
            print(f"Show symbol_info(\"{symbol}\")._asdict():")
            symbol_info_dict = mt.symbol_info(f"{symbol}")._asdict()
            for prop in symbol_info_dict:
                print("  {}={}".format(prop, symbol_info_dict[prop]))

    def order_get_symbol(self, symbol):
        # display data on active orders on symbol
        orders = mt.orders_get(symbol=f"{symbol}")
        if orders is None:
            print("No orders on {}, error code={}".format(symbol, mt.last_error()))
        else:
            print(f"Total orders on {symbol}:", len(orders))
            # display all active orders
            for order in orders:
                print(order)
        print()

    def order_get_group(self, group):
        # get the list of orders on symbols whose names contain "*GBP*"
        gbp_orders = mt.orders_get(group=f"*{group}*")
        if gbp_orders is None:
            print("No orders with group=\"*{}*\", error code={}".format(group, mt.last_error()))
        else:
            print("orders_get(group=\"*{}*\")={}".format(group, len(gbp_orders)))
            if len(gbp_orders) > 0:
                # display these orders as a table using pandas.DataFrame
                df = pd.DataFrame(gbp_orders, columns=gbp_orders[0]._asdict().keys())
                df.drop(['time_done', 'time_done_msc', 'position_id', 'position_by_id', 'reason', 'volume_initial',
                         'price_stoplimit'], axis=1, inplace=True)
                df['time_setup'] = pd.to_datetime(df['time_setup'], unit='s')
                print(df)
            else:
                print("No orders found for group=\"*{}*\"".format(group))

    def order_check(self, symbol):
        # get account currency
        account_currency = mt.account_info().currency
        print("Account currency:", account_currency)

        # prepare the request structure
        symbol = str(symbol)
        symbol_info = mt.symbol_info(symbol)
        if symbol_info is None:
            print(symbol, "not found, can not call order_check()")
            mt.shutdown()
            quit()

        # if the symbol is unavailable in MarketWatch, add it
        if not symbol_info.visible:
            print(symbol, "is not visible, trying to switch on")
            if not mt.symbol_select(symbol, True):
                print("symbol_select({}}) failed, exit", symbol)
                mt.shutdown()
                quit()

        # prepare the request
        point = mt.symbol_info(symbol).point
        request = {
            "action": mt.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": 1.0,
            "type": mt.ORDER_TYPE_BUY,
            "price": mt.symbol_info_tick(symbol).ask,
            "sl": mt.symbol_info_tick(symbol).ask - 100 * point,
            "tp": mt.symbol_info_tick(symbol).ask + 100 * point,
            "deviation": 10,
            "magic": 234000,
            "comment": "python script",
            "type_time": mt.ORDER_TIME_GTC,
            "type_filling": mt.ORDER_FILLING_RETURN,
        }

        # perform the check and display the result 'as is'
        result = mt.order_check(request)
        print(result);
        # request the result as a dictionary and display it element by element
        result_dict = result._asdict()
        for field in result_dict.keys():
            print("   {}={}".format(field, result_dict[field]))
            # if this is a trading request structure, display it element by element as well
            if field == "request":
                traderequest_dict = result_dict[field]._asdict()
                for tradereq_filed in traderequest_dict:
                    print("       traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))

    def order_send(self, symbol):
        # prepare the buy request structure
        symbol = str(symbol)
        symbol_info = mt.symbol_info(symbol)
        if symbol_info is None:
            print(symbol, "not found, can not call order_check()")
            mt.shutdown()
            quit()

        # if the symbol is unavailable in MarketWatch, add it
        if not symbol_info.visible:
            print(symbol, "is not visible, trying to switch on")
            if not mt.symbol_select(symbol, True):
                print("symbol_select({}}) failed, exit", symbol)
                mt.shutdown()
                quit()

        lot = 0.1
        point = mt.symbol_info(symbol).point
        price = mt.symbol_info_tick(symbol).ask
        deviation = 20
        request = {
            "action": mt.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt.ORDER_TYPE_BUY,
            "price": price,
            "sl": price - 100 * point,
            "tp": price + 100 * point,
            "deviation": deviation,
            "magic": 234000,
            "comment": "python script open",
            "type_time": mt.ORDER_TIME_GTC,
            "type_filling": mt.ORDER_FILLING_RETURN,
        }

        # send a trading request
        result = mt.order_send(request)
        # check the execution result
        print("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol, lot, price, deviation));
        if result.retcode != mt.TRADE_RETCODE_DONE:
            print("2. order_send failed, retcode={}".format(result.retcode))
            # request the result as a dictionary and display it element by element
            result_dict = result._asdict()
            for field in result_dict.keys():
                print("   {}={}".format(field, result_dict[field]))
                # if this is a trading request structure, display it element by element as well
                if field == "request":
                    traderequest_dict = result_dict[field]._asdict()
                    for tradereq_filed in traderequest_dict:
                        print("       traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))
            print("shutdown() and quit")
            mt.shutdown()
            quit()

        print("2. order_send done, ", result)
        print("   opened position with POSITION_TICKET={}".format(result.order))
        print("   sleep 2 seconds before closing position #{}".format(result.order))
        time.sleep(2)
        # create a close request
        position_id = result.order
        price = mt.symbol_info_tick(symbol).bid
        deviation = 20
        request = {
            "action": mt.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt.ORDER_TYPE_SELL,
            "position": position_id,
            "price": price,
            "deviation": deviation,
            "magic": 234000,
            "comment": "python script close",
            "type_time": mt.ORDER_TIME_GTC,
            "type_filling": mt.ORDER_FILLING_RETURN,
        }
        # send a trading request
        result = mt.order_send(request)
        # check the execution result
        print("3. close position #{}: sell {} {} lots at {} with deviation={} points".format(position_id, symbol, lot,
                                                                                             price, deviation));
        if result.retcode != mt.TRADE_RETCODE_DONE:
            print("4. order_send failed, retcode={}".format(result.retcode))
            print("   result", result)
        else:
            print("4. position #{} closed, {}".format(position_id, result))
            # request the result as a dictionary and display it element by element
            result_dict = result._asdict()
            for field in result_dict.keys():
                print("   {}={}".format(field, result_dict[field]))
                # if this is a trading request structure, display it element by element as well
                if field == "request":
                    traderequest_dict = result_dict[field]._asdict()
                    for tradereq_filed in traderequest_dict:
                        print("       traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))

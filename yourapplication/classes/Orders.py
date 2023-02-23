# Author:
# Date:
# Email:
# Description:
import datetime
import json
import time

import dateutil.relativedelta


class Orders:

    def __init__(self, order_number):
        self.order_number = order_number
        self.equity_symbol = None

        self.buy_date = None
        self.buy_quantity = None
        self.buy_unit_price = None
        self.total_buy_price = None

        self.sell_date = None
        self.sell_quantity = None
        self.sell_unit_price = None
        self.total_sell_price = None

        self.profit_loss = None
        self.rolling_profit_loss = None
        self.holding_time = None

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                   MEMBER ATTRIBUTE SETTERS                              #
    #                                                                         #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def set_buy_date(self, epoch_buy_time):
        self.buy_date = epoch_buy_time

    def set_sell_date(self, epoch_sell_time):
        self.sell_date = epoch_sell_time

    def set_buy_quantity(self, buy_quantity):
        self.buy_quantity = buy_quantity

    def set_sell_quantity(self, sell_quantity):
        self.sell_quantity = sell_quantity

    def set_holding_time(self, time_delta):
        self.holding_time = time_delta

    def set_buy_unit_price(self, unit_price):
        self.buy_unit_price = round(unit_price, 2)

    def set_sell_unit_price(self, unit_price):
        self.sell_unit_price = round(unit_price, 2)

    def set_total_buy_price(self, total_buy_price):
        self.total_buy_price = total_buy_price

    def set_total_sell_price(self, total_sell_price):
        self.total_sell_price = total_sell_price

    def set_order_profit_loss(self, profit_loss):
        self.profit_loss = profit_loss

    def set_equity_symbol(self, equity_symbol):
        self.equity_symbol = equity_symbol

    def set_rolling_profit_loss(self, rolling_profit_loss):
        self.rolling_profit_loss = round(rolling_profit_loss, 2)

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                   Converters                                            #
    #                                                                         #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def convert_epoch_to_local(self, epoch_time):
        """ Converts epoch time to local time in the format %m-%d-%Y """

        return time.strftime("%m-%d-%Y", time.localtime(epoch_time))

    def convert_symbol_to_simple(self, equity_symbol):

        return equity_symbol.split()[0]

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                   Calculators                                           #
    #                                                                         #
    #                                                                         #
    #                                                                         #
    ###########################################################################
    def calc_holding_time_days(self, start_time, end_time):
        """ Calculates the number of days between two epoch time """
        end_time = datetime.datetime.fromtimestamp(end_time)
        start_time = datetime.datetime.fromtimestamp(start_time)
        delta = end_time - start_time
        return delta.days

    def calc_total_buy_price(self):
        return round(self.buy_quantity * self.buy_unit_price, 2)

    def calc_total_sell_price(self):
        return round(self.sell_quantity * self.sell_unit_price, 2)

    def calc_profit_loss(self):
        return round(self.total_sell_price - self.total_buy_price, 2)

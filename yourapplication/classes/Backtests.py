import json
import os
from datetime import datetime
import re

from yourapplication.classes.Database import Database
from yourapplication.classes.Orders import Orders


class Backtest:

    def __init__(self, **kwargs):
        # Required attribute for inserting backtests into db
        self.__BACKTEST_DEBUG_SWITCH = True
        self.backtest_filename = kwargs.get('backtest_filename', None)
        # Not required
        self.backtest_order_events_filename = kwargs.get(
                'backtest_order_events_filename', None)
        # Required attribute for inserting backtests into db
        self.project_id = kwargs.get('project_id', None)
        # Auto-incremented for inserts. Required for Selects
        self.backtest_id = kwargs.get('backtest_id', None)
        # Required attribute for inserting backtests into db
        self.backtest_name = kwargs.get('backtest_name', None)

        # get any runtime configurations
        self.algorithm_config_filepath = kwargs.get(
                'algorithm_config_filepath', None)
        self.configuration_parameters = kwargs.get('configuration_parameters',
                                                   None)
        self.configuration_ticker = None
        self.configuration_start_date = False
        self.configuration_start_date_year = None
        self.configuration_start_date_month = None
        self.configuration_start_date_day = None
        self.configuration_end_date = False
        self.configuration_end_date_year = None
        self.configuration_end_date_month = None
        self.configuration_end_date_day = None
        self.configuration_id = None

        if self.configuration_parameters is not None:
            print(
                    "=========== GOING TO SET CONFIG PARAMETERS ======== ") if self.__BACKTEST_DEBUG_SWITCH else 0
            self.set_configuration_parameters()
            self.write_configurations_to_config()
            self.insert_configuration_query()

        # -----------------------------------------##
        # Backtesting attributes. These are the different fields returned
        #  to the backtest json file
        # __raw represents the raw json data from the db
        # table represents the data stored in a dictionary
        # -----------------------------------------##
        self.orders_list = []

        self.rolling_window = None

        self.total_performance = None
        self.formatted_trade_statistics = {}

        self.alpha_runtime_statistics = None
        self.formatted_alpha_runtime_statistics = {
                'Mean Population Score'            : {
                        'Date'           : "",
                        'Time'           : "",
                        'Direction'      : None,
                        'Magnitude'      : None,
                        'Is Final Score?': None
                },
                'Rolling Averaged Population Score': {
                        'Date'           : "",
                        'Time'           : "",
                        'Direction'      : None,
                        'Magnitude'      : None,
                        'Is Final Score?': None
                },
                'Long Short Ratio'                 : None,
                'Fitness Score'                    : None,
                'Portfolio Turnover'               : None,
                'Return Over Max Drawdown'         : None,
                'Sortino Ratio'                    : None
        }

        self.charts = None

        self.orders = None

        self.profit_loss = None
        self.formatted_profit_loss = {
                'Date' : [],
                'Time' : [],
                'Value': []
        }

        self.statistics = None
        self.formatted_statistics = {
                'Total Trades'               : None,
                'Average Win'                : None,
                'Average Loss'               : None,
                'Compounding Annual Return'  : None,
                'Drawdown'                   : None,
                'Expectancy'                 : None,
                'Net Profit'                 : None,
                'Sharpe Ratio'               : None,
                'Probabilistic Sharpe Ratio' : None,
                'Loss Rate'                  : None,
                'Win Rate'                   : None,
                'Profit-Loss Ratio'          : None,
                'Alpha'                      : None,
                'Beta'                       : None,
                'Annual Standard Deviation'  : None,
                'Annual Variance'            : None,
                'Information Ratio'          : None,
                'Tracking Error'             : None,
                'Treynor Ratio'              : None,
                'Total Fees'                 : None,
                'Estimated Strategy Capacity': None,
                'Lowest Capacity Asset'      : None
        }

        self.runtime_statistics = None
        self.formatted_runtime_statistics = {
                'Capacity'                  : None,  # Dollar amount (millions)
                'Equity'                    : None,  # Dollar amount
                'Fees'                      : None,  # Dollar amount
                'Holdings'                  : None,  # Dollar amount
                'Net Profit'                : None,  # Dollar amount
                'Probabilistic Sharpe Ratio': None,  # Percentage
                'Return'                    : None,  # Percentage
                'Unrealized'                : None,  # Dollar amount
                'Volume'                    : None  # Dollar amount
        }

        self.algorithm_configuration = None

        self.backtest_order_events = None

        self.formatted_orders_table = []

        self.formatted_total_orders_stats = {
                'Total Profit/Loss'   : None,
                'Average Holding Time': None
        }

        self.total_profit_loss = 0
        self.average_holding_period = 0

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                        OBJECT MANAGEMENT                                #
    #                                                                         #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def run_backtest(self, project_root_filepath):
        # Run a backtest with a directed output
        # 'lean backtest <project> [options]'

        command = ""
        command = f'lean backtest "{project_root_filepath}" ' \
                  f'--output "{self.backtest_filename}"'

        os.system(command)

    def write_configurations_to_config(self):
        """ Writes the configuration parameters to the project config file """
        print(
                "========== READING AND WRITING ALGO CONFIGS ======= ") if self.__BACKTEST_DEBUG_SWITCH else 0

        # Open the configuration_file
        if self.configuration_parameters is not None:
            # Open the config file
            with open(self.algorithm_config_filepath, 'r') as fp:
                print(
                        "=========OPENED CONFIG FILE ========== ") if self.__BACKTEST_DEBUG_SWITCH else 0
                config_file_data = json.load(fp)
                # Access the 'parameters' index and write key, value to parameters
                if self.configuration_ticker is not None:
                    config_file_data['parameters'][
                        'ticker'] = self.configuration_ticker

                if self.configuration_start_date:
                    config_file_data['parameters'][
                        'start_date_year'] = self.configuration_start_date_year
                    config_file_data['parameters'][
                        'start_date_month'] = self.configuration_start_date_month
                    config_file_data['parameters'][
                        'start_date_day'] = self.configuration_start_date_day

                if self.configuration_end_date:
                    config_file_data['parameters'][
                        'end_date_year'] = self.configuration_end_date_year
                    config_file_data['parameters'][
                        'end_date_month'] = self.configuration_end_date_month
                    config_file_data['parameters'][
                        'end_date_day'] = self.configuration_end_date_day

            with open(self.algorithm_config_filepath, 'w') as fp:
                # update the config file
                print(
                        f"=========WRITING TO CONFIG {self.configuration_ticker, self.configuration_start_date, self.configuration_end_date} ========== ") if self.__BACKTEST_DEBUG_SWITCH else 0
                json.dump(config_file_data, fp)

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                       DB INTERACTIONS                                   #
    #                                                                         #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def insert_backtest_query(self):
        """
        Inserts backtest attributes into DB with required FK project_id
        """

        # Format the data for SQL entry
        print('=================== CONVERTING DATA TO JSON in '
              'Backtests.insert_backtest_query================') if self.__BACKTEST_DEBUG_SWITCH else 0
        self.convert_backtest_to_string_for_db()

        # Connect to the database
        db_conn = Database()
        db_conn.connect_to_database()

        # Project_id, backtest_name, backtest_filepath required NOT NULL
        insert_data = (
                self.project_id,
                self.configuration_id,
                self.backtest_name,
                self.backtest_order_events_filename,
                self.backtest_filename,
                self.algorithm_config_filepath,
                self.rolling_window,
                self.total_performance,
                self.alpha_runtime_statistics,
                self.charts,
                self.orders,
                self.profit_loss,
                self.statistics,
                self.runtime_statistics,
                self.algorithm_configuration,
                self.backtest_order_events)

        print(
                '=================== QUERYING RUN ================') if self.__BACKTEST_DEBUG_SWITCH else 0
        backtest_id = db_conn.insert_backtest_query(insert_data).lastrowid
        self.set_backtest_id(backtest_id)

    def select_backtest_from_db(self):
        """
        Selects all attributes of a record Backtest
        """
        # Connect to the database

        db_conn = Database()
        db_conn.connect_to_database()

        # get the data from the DB
        print(
                '=================== PULLING DATA ================') if self.__BACKTEST_DEBUG_SWITCH else 0
        backtest_pull_data = db_conn.select_backtest_from_id_query(
                self.backtest_id)
        backtest_pull_data = list(backtest_pull_data[0])

        # convert and store the query results to backtest attributes as
        # dictionary objects
        print(
                '=================== CONVERTING DATA TO MEMBER ATTRIBUTES ================') if self.__BACKTEST_DEBUG_SWITCH else 0
        self.convert_attributes_to_dictionary_from_db(backtest_pull_data)

    def insert_configuration_query(self):
        db_conn = Database()
        db_conn.connect_to_database()
        print(
                '=================== INSERTING CONFIGURATIONS ================') if self.__BACKTEST_DEBUG_SWITCH else 0
        print("configuration parameters and type ",
              self.configuration_parameters,
              type(self.configuration_parameters))
        print('configuration_file path ', self.algorithm_config_filepath)

        self.configuration_id = db_conn.insert_configurations_query((
                json.dumps(self.configuration_parameters),
                self.algorithm_config_filepath)).lastrowid

        # update the intersection table
        self.insert_project_configurations_query()

    def insert_project_configurations_query(self):
        db_conn = Database()
        db_conn.connect_to_database()
        print(
                '=================== INSERTING PROJECT_CONFIGURATIONS INTERSECTION TABLE ================ config id and project_id',
                self.configuration_id,
                self.project_id) if self.__BACKTEST_DEBUG_SWITCH else 0

        db_conn.insert_project_configurations_query(
                (self.configuration_id, self.project_id))

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                       DATA CONVERTERS                                   #
    #                                                                         #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def convert_attributes_to_dictionary_from_db(self, backtest_pull_data):
        """
        Converts the backtest select query from string to dictionary values and stores in
        member attribute
        """
        print(
                "============ CONVERTING BACKTEST ATTRIBUTES TO DICTIONARY FROM DB ==========") if self.__BACKTEST_DEBUG_SWITCH else 0

        # convert null fields to empty dictionaries and convert dictionary data to json dictionary
        for i in range(7, len(backtest_pull_data)):
            if backtest_pull_data[i] is None:
                backtest_pull_data[i] = {}
            else:
                backtest_pull_data[i] = json.loads(backtest_pull_data[i])

        self.set_backtest_id(backtest_pull_data[0])
        self.set_project_id(backtest_pull_data[1])
        self.set_configuration_id(backtest_pull_data[2])
        self.set_backtest_name(backtest_pull_data[3])
        self.set_backtest_order_events_filename(backtest_pull_data[4])
        self.set_backtest_filename(backtest_pull_data[5])
        self.set_algorithm_config_filepath(backtest_pull_data[6])
        self.set_rolling_window(backtest_pull_data[7])
        self.set_total_performance(backtest_pull_data[8])
        self.set_alpha_runtime_statistics(backtest_pull_data[9])
        self.set_charts(backtest_pull_data[10])
        self.set_orders(backtest_pull_data[11])
        self.set_profit_loss(backtest_pull_data[12])
        self.set_statistics(backtest_pull_data[13])
        self.set_runtime_statistics(backtest_pull_data[14])
        self.set_algorithm_configuration(backtest_pull_data[15])
        if self.backtest_order_events_filename is not None:
            self.set_backtest_order_events(backtest_pull_data[16])
        else:
            # There are no back test order events to load from the DB
            self.backtest_order_events = None

    def convert_backtest_to_string_for_db(self):
        """
        Converts Backtest parameters to json objects for SQL insertion and returns
        them as a list of JSON objects
        """
        print(
                '=================== OPENING BT FILE ================') if self.__BACKTEST_DEBUG_SWITCH else 0
        with open(self.backtest_filename) as bt_file:
            data = json.load(bt_file)

            if 'RollingWindow' in data:
                self.rolling_window = json.dumps(data["RollingWindow"])
            else:
                self.rolling_window = None
            if 'TotalPerformance' in data:
                self.total_performance = json.dumps(data['TotalPerformance'])
            else:
                self.total_performance = None
            if 'AlphaRuntimeStatistics' in data:
                self.alpha_runtime_statistics = json.dumps(
                        data['AlphaRuntimeStatistics'])
            else:
                self.alpha_runtime_statistics = None
            if 'Charts' in data:
                self.charts = json.dumps(data['Charts'])
            else:
                self.charts = None
            if 'Orders' in data:
                self.orders = json.dumps(data['Orders'])
            else:
                self.orders = None
            if 'ProfitLoss' in data:
                self.profit_loss = json.dumps(data['ProfitLoss'])
            else:
                self.profit_loss = None
            if 'Statistics' in data:
                self.statistics = json.dumps(data['Statistics'])
            else:
                self.statistics = None
            if 'RuntimeStatistics' in data:
                self.runtime_statistics = json.dumps(data['RuntimeStatistics'])
            else:
                self.runtime_statistics = None

            if 'AlgorithmConfiguration' in data:
                self.algorithm_configuration = json.dumps(
                        data['AlgorithmConfiguration'])
            else:
                self.algorithm_configuration = None

        # backtest order events are sourced from a separate file
        if self.backtest_order_events_filename is not None:
            print(
                    '=================== OPENING BT ORDERS EVENTS FILE ================') if self.__BACKTEST_DEBUG_SWITCH else 0
            with open(self.backtest_order_events_filename) as btoe_file:
                data = json.load(btoe_file)
                self.backtest_order_events = json.dumps(data)
        else:
            # There are no back test order events to load from file
            pass

    def convert_order_events_to_orders(self):
        """ Converts the order_events.json to a list of buy/sell orders objects """
        order_count = 1
        rolling_profit_loss = 0

        for event in self.backtest_order_events:
            # buy order executed
            if event['direction'] == 'buy' and event['status'] == 'filled':
                new_order = Orders(order_count)
                order_count += 1

                # update the equity symbol, buy time, quantity, buy unit price, total buy cost
                new_order.set_equity_symbol(
                        new_order.convert_symbol_to_simple(event['symbol']))
                new_order.set_buy_date(event['time'])
                new_order.set_buy_quantity(int(abs(event['fill-quantity'])))
                new_order.set_buy_unit_price(event['fill-price'])
                new_order.set_total_buy_price(new_order.calc_total_buy_price())

                # add new order to list of orders
                print("=====ADDING NEW ORDER OBJECT TO ORDERS_LIST======")
                self.orders_list.append(new_order)

            # update new order with sell data
            elif event['direction'] == 'sell' and event['status'] == 'filled':

                # update the sell date, quantity, unit price
                new_order.set_sell_date(event['time'])
                new_order.set_sell_quantity(int(abs(event['fill-quantity'])))
                new_order.set_sell_unit_price(event['fill-price'])

                # calculate and store the holding time in days
                holding_time_days = new_order.calc_holding_time_days(
                        new_order.buy_date, new_order.sell_date)
                new_order.set_holding_time(holding_time_days)

                # calculate and store total buy price
                new_order.set_total_sell_price(
                        new_order.calc_total_sell_price())

                # update the profit/loss
                new_order.set_order_profit_loss(new_order.calc_profit_loss())
                rolling_profit_loss += new_order.profit_loss
                new_order.set_rolling_profit_loss(rolling_profit_loss)

            # skip order events that aren't actual buys or sells
            else:
                continue

    def separate_date_to_day_month_year(self, date):
        """
        Separates a string YYYY-MM-DD into int values for each year, month, day
        """
        date_fields = date.split('-')
        year = int(date_fields[0])
        month = int(date_fields[1])
        day = int(date_fields[2])

        return year, month, day

    def calculate_total_profit_loss(self):
        total_profit_loss = 0
        for order in self.orders_list:
            if order.profit_loss is not None:
                print('running profit loss', total_profit_loss)
                total_profit_loss += order.profit_loss

        return round(total_profit_loss, 2)

    def calculate_avg_holding_time(self):
        holding_time = 0
        orders_count = 0

        for order in self.orders_list:
            if order.holding_time is not None:
                holding_time += order.holding_time
                orders_count += 1

        if orders_count != 0:
            self.average_holding_period = holding_time // orders_count

        return round(self.average_holding_period, 2)

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                   MEMBER ATTRIBUTE SETTERS                              #
    #                                                                         #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def set_backtest_id(self, backtest_id):
        self.backtest_id = backtest_id

    def set_project_id(self, project_id):
        self.project_id = project_id

    def set_configuration_id(self, configuration_id):
        self.configuration_id = configuration_id

    def set_backtest_name(self, backtest_name):
        self.backtest_name = backtest_name

    def set_backtest_order_events_filename(self,
                                           backtest_order_events_filename):
        """ Sets the file path for the given backtest's order events"""
        self.backtest_order_events_filename = backtest_order_events_filename
        if self.backtest_order_events_filename:
            self.make_simple_orders_table()
            self.make_total_orders_stats()

    def set_backtest_filename(self, backtest_filename):
        """ Sets the file path for the given backtest"""
        self.backtest_filename = backtest_filename

    def set_algorithm_config_filepath(self, config_filepath):
        self.algorithm_config_filepath = config_filepath

    def set_rolling_window(self, rolling_window_json_object):
        self.rolling_window = rolling_window_json_object

    def set_total_performance(self, total_performance_json_object):
        self.total_performance = total_performance_json_object

    def set_alpha_runtime_statistics(self,
                                     alpha_runtime_statistics_json_object):
        """
        Stores the alpha runtime statistics stats in their member attribute.
        Creates a formatted alpha runtime statistics table
        """
        self.alpha_runtime_statistics = alpha_runtime_statistics_json_object
        if self.backtest_filename:
            self.__format_alpha_runtime_statistics_table()

    def set_charts(self, charts_json_object):
        self.charts = charts_json_object

    def set_orders(self, orders_json_object):
        self.orders = orders_json_object

    def set_profit_loss(self, profit_loss_json_object):
        """
        Stores the profit loss stats in their member attribute.
        Creates a formatted profit loss table
        """
        self.profit_loss = profit_loss_json_object
        if self.backtest_filename:
            self.__format_profit_loss_table()

    def set_statistics(self, statistics_json_object):
        """
        Stores the statistics stats in their member attribute.
        Creates a formatted statistics table
        """
        self.statistics = statistics_json_object
        if self.backtest_filename:
            self.__format_statistics_table()

    def set_runtime_statistics(self, runtime_statistics_json_object):
        """
           Stores the runtime statistics stats in their member attribute.
           Creates a formatted runtime statistics table
        """
        self.runtime_statistics = runtime_statistics_json_object
        if self.backtest_filename:
            self.__format_runtime_statistics_table()

    def set_algorithm_configuration(self, algorithm_configuration_json_object):
        self.algorithm_configuration = algorithm_configuration_json_object

    def set_backtest_order_events(self, backtest_order_events_json_object):
        self.backtest_order_events = backtest_order_events_json_object
        if self.backtest_order_events:
            print("=======******* CONVERTING SIMPLE ORDERS TABLE =====*******")
            self.convert_order_events_to_orders()
            self.make_simple_orders_table()
            self.make_total_orders_stats()

    def set_configuration_parameters(self):
        print(
                f"=========== SETTING CONFIG PARAMETERS ======== , {self.configuration_parameters}") if self.__BACKTEST_DEBUG_SWITCH else 0
        print(type(self.configuration_parameters))
        if 'ticker' in self.configuration_parameters:
            self.configuration_ticker = self.configuration_parameters['ticker']

        if 'start_date' in self.configuration_parameters:
            self.configuration_start_date = True
            config_year, config_month, config_day = self.separate_date_to_day_month_year(
                    self.configuration_parameters[
                        'start_date'])
            self.configuration_start_date_year = config_year
            self.configuration_start_date_month = config_month
            self.configuration_start_date_day = config_day

        if 'end_date' in self.configuration_parameters:
            self.configuration_end_date = True
            config_year, config_month, config_day = self.separate_date_to_day_month_year(
                    self.configuration_parameters[
                        'end_date'])
            self.configuration_end_date_year = config_year
            self.configuration_end_date_month = config_month
            self.configuration_end_date_day = config_day

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                           TABLE FORMATTERS                              #
    #                                                                         #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def __format_profit_loss_table(self):
        """
        Formats the Profit Loss Table values:
            - Converts datetime strings to date and time individual strings.
            - rounds the profit loss value to 2 decimals
            - Stores the multiple records in their own list for easy appending
                in jinja template
        """
        print(
                '=================== MAKING FORMATTED PROFIT LOSS ================') if self.__BACKTEST_DEBUG_SWITCH else 0
        if type(self.profit_loss) is not dict:
            profit_loss = json.loads(self.profit_loss)
        else:
            profit_loss = self.profit_loss

        for key, value in profit_loss.items():
            time_stamp = datetime.strptime(str(key), "%Y-%m-%dT%H:%M:%SZ")
            time = time_stamp.time()
            date = time_stamp.date()

            self.formatted_profit_loss['Date'].append(str(date))
            self.formatted_profit_loss['Time'].append(str(time))
            self.formatted_profit_loss['Value'].append(round(value, 2))

    def __format_statistics_table(self):
        """
        Formats the Statistics Table values:
            - Converts string values to float values.
            - Removes percent signs and represents percents as decimal values
                    rounded to 4 places
            - Removes $ in front of currencies and stores value as float
        """

        print(
                '=================== MAKING FORMATTED STATSITICS ================') if self.__BACKTEST_DEBUG_SWITCH else 0
        if type(self.statistics) is not dict:
            statistics = json.loads(self.statistics)
        else:
            statistics = self.statistics
        for key, value in statistics.items():
            if '%' in value:
                value = re.sub('%', '', value)
                value = float(value)
                value = round(value / 100, 4)
                self.formatted_statistics[key] = value
            elif '$' in value:
                value = re.sub(r'[,$M]', '', value)
                value = float(value)
                value = round(value, 2)
                self.formatted_statistics[key] = value
            elif key == 'Lowest Capacity Asset':
                self.formatted_statistics[key] = value
            else:
                self.formatted_statistics[key] = float(value)

    def __format_alpha_runtime_statistics_table(self):
        """
        Formats the Alpha Runtime Statistics Table values:
            - Converts datetime utc string to date and time individually
            - Renames the attributes using Title Casing instead of camelCasing.
        """
        print(
                '=================== MAKING FORMATTED ALPHA RUNTIME STATS ================') if self.__BACKTEST_DEBUG_SWITCH else 0
        if type(self.alpha_runtime_statistics) is not dict:
            alpha_runtime_statistics = json.loads(
                    self.alpha_runtime_statistics)
        else:
            alpha_runtime_statistics = self.alpha_runtime_statistics
        for key, value in alpha_runtime_statistics.items():
            if key == 'MeanPopulationScore' or key == 'RollingAveragedPopulationScore':
                if key == 'MeanPopulationScore':
                    key = 'Mean Population Score'
                else:
                    key = 'Rolling Averaged Population Score'

                for key2, value2 in value.items():
                    if key2 == 'UpdatedTimeUtc':
                        time_stamp = datetime.strptime(str(value2),
                                                       "%Y-%m-%dT%H:%M:%S")
                        time = time_stamp.time()
                        date = time_stamp.date()
                        self.formatted_alpha_runtime_statistics[key][
                            'Date'] = str(date)
                        self.formatted_alpha_runtime_statistics[key][
                            'Time'] = str(time)

                    else:
                        if key2 == 'IsFinalScore':
                            key2 = 'Is Final Score?'

                        self.formatted_alpha_runtime_statistics[key][
                            key2] = value2

            # Reformat remaining key names and store values -- these values do
            # not need any further formatting
            else:
                if key == "LongShortRatio":
                    key = 'Long Short Ratio'
                if key == "FitnessScore":
                    key = 'Fitness Score'
                if key == "PortfolioTurnover":
                    key = 'Portfolio Turnover'
                if key == "ReturnOverMaxDrawdown":
                    key = 'Return Over Max Drawdown'
                if key == "SortinoRatio":
                    key = 'Sortino Ratio'

                self.formatted_alpha_runtime_statistics[key] = value

    def __format_runtime_statistics_table(self):
        """
        Formats the Runtime Statistics table values:
                - Removes $ and % symbols and stores values as floats
                - Stores percents as decimal values (ratio 1: )
        """

        print(
                '=================== MAKING FORMATTED RUNTIME STATS ================') if self.__BACKTEST_DEBUG_SWITCH else 0
        if type(self.runtime_statistics) is not dict:
            runtime_statistics = json.loads(
                    self.runtime_statistics)
        else:
            runtime_statistics = self.runtime_statistics

        for key, value in runtime_statistics.items():
            if '%' in value:
                value = re.sub(r'[,%]', '', value)
                value = float(value)
                value = round(value / 100, 4)
            elif '$' in value:
                value = re.sub(r'[,$MBK]', '', value)
                value = float(value)
                value = round(value, 2)
            else:
                value = re.sub(',', '', value)
                value = float(value)

            self.formatted_runtime_statistics[key] = value

    def make_orders_table(self) -> dict:
        """
        Converts the orders to a list of values for populating an HTML table
        """
        if type(self.orders) is not dict:
            orders = json.loads(
                    self.orders)
        else:
            orders = self.orders
        print(
                '=================== MAKING FORMATTED ORDERS ================') if self.__BACKTEST_DEBUG_SWITCH else 0
        orders = json.loads(self.orders)
        orders_list = {"Type"    : [], "Symbol": [], "Price": [], "Time": [],
                       "Quantity": [], "Status": [], "Value": [],
                       "BidPrice": [], "AskPrice": [], "LastPrice": []}

        for key, value in orders.items():
            orders_list['Type'].append(value["Type"])
            orders_list['Symbol'].append(value["Symbol"]["Value"])
            orders_list['Price'].append(value["Price"])
            orders_list['Time'].append(value["Time"])
            orders_list['Quantity'].append(value["Quantity"])
            orders_list['Status'].append(value["Status"])
            orders_list['Value'].append(value["Value"])
            orders_list['BidPrice'].append(
                    value["OrderSubmissionData"]["BidPrice"])
            orders_list['AskPrice'].append(
                    value["OrderSubmissionData"]["AskPrice"])
            orders_list['LastPrice'].append(
                    value["OrderSubmissionData"]["LastPrice"])

        return orders_list

    def make_trade_statistics_table(self) -> dict:
        """
        Converts total performance to a table
        """
        self.formatted_trade_statistics = self.total_performance['TradeStatistics']

        decimal_time = self.formatted_trade_statistics['AverageTradeDuration']
        days = decimal_time.split(':')[0]
        self.formatted_trade_statistics['AverageTradeDuration'] = days

        decimal_time = self.formatted_trade_statistics['AverageWinningTradeDuration']
        days = decimal_time.split(':')[0]
        self.formatted_trade_statistics['AverageWinningTradeDuration'] = days

        decimal_time = self.formatted_trade_statistics[
            'AverageLosingTradeDuration']
        days = decimal_time.split(':')[0]
        self.formatted_trade_statistics['AverageLosingTradeDuration'] = days

        decimal_time = self.formatted_trade_statistics[
            'MedianTradeDuration']
        days = decimal_time.split(':')[0]
        self.formatted_trade_statistics['MedianTradeDuration'] = days

        decimal_time = self.formatted_trade_statistics[
            'MedianWinningTradeDuration']
        days = decimal_time.split(':')[0]
        self.formatted_trade_statistics['MedianWinningTradeDuration'] = days

        decimal_time = self.formatted_trade_statistics[
            'MedianLosingTradeDuration']
        days = decimal_time.split(':')[0]
        self.formatted_trade_statistics['MedianLosingTradeDuration'] = days

        decimal_time = self.formatted_trade_statistics[
            'MaximumDrawdownDuration']
        days = decimal_time.split(':')[0]
        self.formatted_trade_statistics['MaximumDrawdownDuration'] = days

        return self.formatted_trade_statistics

    def make_charts_table(self) -> dict:
        """
        Converts total performance to a table
        """
        return self.charts

    def make_rolling_window_table(self) -> dict:
        """
        Converts total performance to a table
        """
        return self.rolling_window

    def make_simple_orders_table(self):

        for order in self.orders_list:
            formatted_order_event_entry = {'Order Number'               : order.order_number,
                                           'Symbol'                     : order.equity_symbol,
                                           'Buy Date'                   : order.convert_epoch_to_local(
                                                   order.buy_date),
                                           'Buy Quantity'               : order.buy_quantity,
                                           'Buy Unit Cost'              : order.buy_unit_price,
                                           'Total Buy Cost'             : order.total_buy_price,
                                           'Sell Date'                  : order.convert_epoch_to_local(
                                                   order.sell_date),
                                           'Sell Quantity'              : order.sell_quantity,
                                           'Sell Unit Cost'             : order.sell_unit_price,
                                           'Total Sell Cost'            : order.total_sell_price,
                                           'Order Profit/Loss'          : order.profit_loss,
                                           'Order Rolling Profit/Loss'  : order.rolling_profit_loss,
                                           'Order Holding Time (day(s))': order.holding_time}

            self.formatted_orders_table.append(formatted_order_event_entry)

    def make_total_orders_stats(self):
        self.formatted_total_orders_stats[
            'Total Profit/Loss'] = self.calculate_total_profit_loss()
        self.formatted_total_orders_stats[
            'Average Holding Time'] = self.calculate_avg_holding_time()

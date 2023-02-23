# Author:
# Date:
# Email:
# Description: Test file for testing individual functionality
import json

from classes.Backtests import Backtest
from classes.Projects import Project
from plotting.plot import plot_equity
from classes.Plot import Plot
import os

from yourapplication import Database

db_conn = Database()
db_conn.connect_to_database()
backtest_pull_data = db_conn.select_backtest_from_id_query(1)
backtest_pull_data = backtest_pull_data[0]
print((backtest_pull_data[9]))
print(type(json.loads(backtest_pull_data[7])))



for i in range(len(backtest_pull_data)):
    print(type(backtest_pull_data[i]))
    backtest_pull_data[i] = json.dumps(backtest_pull_data[i])
    if backtest_pull_data[i] is None:
        print('nnnooonne')
        backtest_pull_data[i] = {}

print((backtest_pull_data[9]))


# project = Project(algorithm_id=1,
#                   project_name="Test",
#                   project_root_filepath="~/some/file/path/Test",
#                   algorithm_file_path = "~/some/file/path/Test",
#                   algorithm_language = "python")
# project.insert_project_query()
#
# # # New backtest matched with its associated FK project_id
# project_id = 1
# backtest_filename = 'yourapplication/db/sample_backtest_file.json'
# backtest_order_events_filename = 'yourapplication/db/order_events.json'
# backtest = Backtest(project_id=project_id, backtest_filename=backtest_filename, backtest_order_events_filename=backtest_order_events_filename, backtest_name='sample_backtest')
#
# # Sets the file location for the master backtest json file
# backtest.set_backtest_filename(backtest_filename)
#
# # Converts data in json file to individual attributes and then inserts and
# # commits then to the db
# backtest.insert_backtest_query()
#
# # pull backtest with id = 1 from db
#
# # pull stats from the db that match the provided backtest_id
# backtest_id = 1
# backtest_pull = Backtest(backtest_id=backtest_id)
# backtest_pull.select_backtest_from_db()
#
# plot_equity(backtest_pull)
#
# plot = Plot(backtest_id = 1, plot_type = "plot_equity", plot_file_name = "sample_backtest_equity_plot.png", plot_debug_switch = True)
# plot.create_plot()
#
# print(backtest_pull.backtest_order_events[0])
#
# # see the formatted values for different attributes
# for key, value in backtest_pull.alpha_runtime_statistics.items():
#     print(f'{key} : {value}')
#
# for key, value in backtest_pull.formatted_profit_loss.items():
#     print(f'{key} : {value}')
#
# i = 0
# for record in backtest_pull.backtest_order_events:
#     print(f'---------------order # {i}')
#     i += 1
#     for key, value in record.items():
#         print(f'{key} : {value}')
#
# table1 = backtest_pull.make_orders_table()
# table2 = backtest_pull.make_rolling_window_table()
# table3 = backtest_pull.make_total_perf_table()
# table4 = backtest_pull.make_charts_table()
#
# print(table1)
# print(table2)
# print(table3)
# print(table4)
#
# project_pull = project.select_project_query()
# print(project_pull)

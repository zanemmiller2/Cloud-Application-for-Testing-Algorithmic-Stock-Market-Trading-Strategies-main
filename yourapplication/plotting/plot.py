import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
from yourapplication.classes.Backtests import Backtest
import os
from datetime import datetime

# create a module that accepts a set of datapoints and creates a plot of net profit, then returns the path to the plot

def plot_equity(backtest: Backtest):

    print("=====================+ GETTING BACKTEST DATA FOR PLOT ====================")

    data = list(backtest.charts['Strategy Equity']['Series']['Equity']['Values'])

    print("=====================+ MAKING PLOT ====================")
    fig, ax = plt.subplots()

    x = list(map(lambda data : datetime.fromtimestamp(data['x']), data))
    y = list(map(lambda data : data['y'], data))

    ax.plot(x, y)

    ax.set(xlabel="time (date)", ylabel="equity ($)", title="Portfolio Equity Over Time")

    cwd = os.getcwd()
    plot_filename = backtest.backtest_name + '_equity_plot.png'

    if not os.path.exists(cwd + '/yourapplication/plotting/plots'):
        os.mkdir(cwd + '/yourapplication/plotting/plots')

    plt.savefig(str(cwd + '/yourapplication/plotting/plots/' + plot_filename))

    print("=====================+ RETURNING PLOT FILENAME ====================")

    return plot_filename

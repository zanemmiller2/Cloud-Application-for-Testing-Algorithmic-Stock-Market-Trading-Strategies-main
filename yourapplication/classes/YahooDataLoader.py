import yahoo_fin.stock_info as si
import pandas as pd
from pathlib import Path
from datetime import timedelta
import random


def get_yahoo_ticker(ticker, folder, start_date, end_date, reload_data=False, data_to_alter_percent=0, max_alter_percent=0):
    fname = ticker.lower() + '.zip'
    compression_opts = dict(method='zip', archive_name=ticker + '.csv')

    path = Path(folder) / fname

    # If file exists and we don't want fresh data
    if path.exists() and not reload_data:
        df = pd.read_csv(path, index_col=0)
        dates = pd.DatetimeIndex(df.index.sort_values(ascending=True))
    else:
        dates = None

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if dates is None or start_date < dates[0] or end_date > dates[-1]:

        try:
            delta = timedelta(days=3)
            df = si.get_data(ticker, start_date=start_date - delta,
                             end_date=end_date + delta)
            df = df.reset_index()
            df['index'] = df['index'].apply(convert_date_yahoo_to_qc)
            df['open'] = df['open'].apply(lambda x: int(x * 10000))
            df['high'] = df['high'].apply(lambda x: int(x * 10000))
            df['low'] = df['low'].apply(lambda x: int(x * 10000))
            df['close'] = df['close'].apply(lambda x: int(x * 10000))
            df = df.drop(['adjclose', 'ticker'], axis=1)

            randomly_alter_data_item(df, data_to_alter_percent, max_alter_percent)
            
            df.to_csv(path, index=False, header=False,
                      compression=compression_opts)
            return f"{ticker}: Data loaded and put in path - " + str(path)

        except BaseException as e:
            print(e)
            return f"{ticker}: Error loading ticker. Please check dates and ticker name/format is correct"

    else:
        return f"{ticker}: Data already exists for date range. Please select overwrite data for fresh data."


def get_yahoo_data(tickers: list, start_date, end_date, reload_data=False, data_to_alter_percent=0, max_alter_percent=0):
    """Get a list of tickers from yahoo and save them in the Default LEAN data directory"""
    # transform ticekrs into a list
    tickers = tickers if isinstance(tickers, list) else [tickers]
    folder = Path("./yourapplication/projects/data/equity/usa/daily")

    if not folder.exists():
        folder.mkdir()
        print(f'Folder {str(folder)} - Created')
    else:
        print(f'Folder {str(folder)} - Ok')

    loaded_tickers = []
    for ticker in tickers:
        loaded_tickers.append(
            get_yahoo_ticker(ticker, folder, start_date, end_date,
                             reload_data, data_to_alter_percent, max_alter_percent))

    return loaded_tickers


def convert_date_yahoo_to_qc(date):
    date = str(date)
    datelist = date.split(' ')[0].split('-')

    year = datelist[0]
    month = datelist[1]
    day = datelist[2]

    return year + month + day + " 00:00"

def randomly_alter_data_item(df, data_to_alter_percent, max_alter_percent):
    
    df_altered = df.sample(frac = data_to_alter_percent)
    df_altered['open'] = df_altered['open'].apply(lambda x: int(x * random.uniform(1-max_alter_percent, 1+max_alter_percent)))
    df_altered['high'] = df_altered['high'].apply(lambda x: int(x * random.uniform(1-max_alter_percent, 1+max_alter_percent)))
    df_altered['low'] = df_altered['low'].apply(lambda x: int(x * random.uniform(1-max_alter_percent, 1+max_alter_percent)))
    df_altered['close'] = df_altered['close'].apply(lambda x: int(x * random.uniform(1-max_alter_percent, 1+max_alter_percent)))
    df_altered['volume'] = df_altered['volume'].apply(lambda x: int(x * random.uniform(1-max_alter_percent, 1+max_alter_percent)))
    df.update(df_altered)
    
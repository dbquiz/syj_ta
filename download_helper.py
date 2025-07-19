import json
import os
import pandas as pd
import requests
import yfinance as yf


class DataDownloader:
    """
    Manages fetching and storing S&P 500 ticker symbols from Wikipedia.
    """
    WIKIPEDIA_URL = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    DEFAULT_HEADERS = {'User-Agent': 'Mozilla/5.0'}
    DATA_DIR = "data"
    DEFAULT_FILENAME = "sp500_tickers.json"

    def __init__(self, url=None, headers=None):
        """
        Initializes the ticker manager.

        Args:
            url (str, optional): The URL to fetch tickers from. Defaults to Wikipedia.
            headers (dict, optional): Headers for the request. Defaults to a standard User-Agent.
        """
        self.url = url or self.WIKIPEDIA_URL
        self.headers = headers or self.DEFAULT_HEADERS

    def get_ticker_list(self, filepath=None):
        """
        Ensures tickers are available, fetching and saving them if necessary.

        This is the main public method for this class. It will first check
        for a local JSON file of tickers. If it exists and is valid, it
        returns the tickers from the file. Otherwise, it fetches the tickers
        from the source, saves them to the JSON file, and then returns them.

        Args:
            filepath (str, optional): The path to the JSON file. Defaults to
                                      the class default.

        Returns:
            list: A list of S&P 500 ticker symbols, or an empty list on failure.
        """
        if filepath is None:
            filepath = os.path.join(self.DATA_DIR, self.DEFAULT_FILENAME)

        if os.path.exists(filepath):
            tickers = self._load_tickers_from_json(filepath)
            if tickers is not None:
                return tickers
            print(f"File '{filepath}' found but was empty or corrupt. Refetching...")

        tickers = self._fetch_tickers()
        self._save_tickers_to_json(tickers, os.path.basename(filepath))
        return tickers

    def download_weekly_data(self, ticker):
        """
        Downloads weekly historical OHLC data for the last 2 years.

        This is a convenience wrapper around download_historic_data.

        Args:
            ticker (str): The stock ticker symbol.

        Returns:
            pd.DataFrame: A DataFrame containing the OHLC data.
        """
        return self.download_historic_data(ticker, span="2y", interval="1wk")

    def download_daily_data(self, ticker):
        """
        Downloads daily historical OHLC data for the last 1 year.

        This is a convenience wrapper around download_historic_data.

        Args:
            ticker (str): The stock ticker symbol.

        Returns:
            pd.DataFrame: A DataFrame containing the OHLC data.
        """
        return self.download_historic_data(ticker, span="1y", interval="1d")

    def download_historic_data(self, ticker, span="1y", interval="1d"):
        """
        Downloads historical OHLC data for a given ticker using yfinance.

        Args:
            ticker (str): The stock ticker symbol.
            span (str, optional): The time span for the data.
                                  Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max.
                                  Defaults to "1y".
            interval (str, optional): The data interval.
                                      Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo.
                                      Defaults to "1d".

        Returns:
            pd.DataFrame: A DataFrame containing the OHLC data, or an empty
                          DataFrame on failure.
        """
        print(f"\nDownloading {span} of {interval} data for {ticker}...")
        try:
            stock = yf.Ticker(ticker)
            # yfinance returns an empty dataframe for invalid tickers
            # or if no data is found for the period.
            hist_df = stock.history(period=span, interval=interval)
            hist_df = self._flatten_yfinance_columns(hist_df)
            if hist_df.empty:
                print(f"Warning: No data found for ticker '{ticker}' for the given period.")
            return hist_df
        except Exception as e:
            print(f"An error occurred while downloading data for {ticker}: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error


    #===========================================
    # This is specific for yfinance dataframe output. the columns are multiindex - like {[Close, 'JNJ']}
    # this causes lots of index errors when we do column operations.
    # so we just remove the second field of multiindex.

    def _flatten_yfinance_columns(self, df):
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns.values]
        return df
    
    def _fetch_tickers(self):
        """
        Fetches the list of S&P 500 tickers from the configured URL.

        Returns:
            list: A list of S&P 500 ticker symbols.

        Raises:
            requests.exceptions.RequestException: For issues with the network request.
            KeyError: If the expected table or column is not found.
            IndexError: If the expected table is not found.
        """
        print("Fetching S&P 500 component list from Wikipedia...")
        response = requests.get(self.url, headers=self.headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        tables = pd.read_html(response.text)
        sp500_table = tables[0]
        tickers = sp500_table['Symbol'].tolist()
        print(f"Found {len(tickers)} tickers.")
        return tickers

    @staticmethod
    def _save_tickers_to_json(tickers, filename=None):
        """Saves a list of tickers to a JSON file."""
        if filename is None:
            filename = DataDownloader.DEFAULT_FILENAME

        if not os.path.exists(DataDownloader.DATA_DIR):
            os.makedirs(DataDownloader.DATA_DIR)

        filepath = os.path.join(DataDownloader.DATA_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(tickers, f, indent=4)
        print(f"Successfully saved tickers to {filepath}")
        return filepath

    @staticmethod
    def _load_tickers_from_json(filepath=None):
        """Loads a list of tickers from a JSON file."""
        if filepath is None:
            filepath = os.path.join(DataDownloader.DATA_DIR, DataDownloader.DEFAULT_FILENAME)

        print(f"\nLoading tickers from {filepath}...")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tickers = json.load(f)
            print(f"Successfully loaded {len(tickers)} tickers.")
            return tickers
        except FileNotFoundError:
            print(f"Error: The file {filepath} was not found.")
            return None
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {filepath}.")
            return None


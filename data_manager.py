import os
import pandas as pd
from download_helper import DataDownloader
import utility 
import re



class DataManager:
    def __init__(self, ticker_filepath="data/sp500_tickers.json"):
        print("DataManager initializing.")
        self._ticker_filepath = ticker_filepath
        self.weekly_db_path = os.path.join(".", DataDownloader.DATA_DIR, f"weekly_data_{utility.get_date_mmddyyyy()}.db")
        self._weeklydata_ = []
        self._initialize_tickers()
        print(len(self._tickers_))
        self._check_and_update_data_files()
        
    #===========================================

    def get_weekly_data(self, span='2y'):
        if not self._weeklydata_:
            self._prepare_weekly_data_(span)

        return self._weeklydata_

    def get_daily_data(self):
        if not self._dailydata_:
            self._prepare_daily_data_()

        return self._weeklydata_
    
    #===========================================
    def get_close_on_date(self, back_date):
        dd = DataDownloader()
        close_data = []
        for ticker in self._tickers_:
            print(ticker)
            close_data.append((ticker, dd.get_daily_close_on_date(ticker, back_date)))

        return close_data

    def get_yearly_high(self, back_year):
        dd = DataDownloader()
        high_data = []
        for ticker in self._tickers_:
            print(ticker)
            high_data.append((ticker, dd.get_yearly_high(ticker, back_year)))

        return high_data

    def _prepare_daily_data_(self):
        self._daily_data_ = self.load_daily_data_from_sqlite()
        if not self._daily_data_:
            ddata = []
            dd = DataDownloader()
            for ticker in self._tickers_:
                df = dd.download_daily_data(ticker)
                if len(df) > 0:
                    ddata.append((ticker, df))
            self._daily_data_ = ddata
            self.serialize_daily_data_to_sqlite()

    #===========================================
    
    def get_tickers(self):
        return self._tickers_

    #===========================================

    def _prepare_weekly_data_(self, span='2y'):
        self._weekly_data_ = self.load_weekly_data_from_sqlite()
        if not self._weekly_data_:
            print("populating weekly data")
            wdata = []
            dd = DataDownloader()
            print(len(self._tickers_))
            for ticker in self._tickers_:
                df = dd.download_weekly_data(ticker, span=span)
                if len(df) > 0:
                    wdata.append((ticker, df))
            
            print(len(wdata))
            self._weeklydata_ = wdata
            print(len(self._weeklydata_))
            self.serialize_weekly_data_to_sqlite()

    #===========================================

    def _check_and_update_data_files(self):
        """
        Checks for data files with dates in their names (mm_dd_yyyy format).
        If the date in the filename is not today's date, the file is deleted.
        This ensures that data files are refreshed daily.
        """
        today_date_str = utility.get_date_mmddyyyy()
        data_dir = DataDownloader.DATA_DIR # Assuming DATA_DIR is accessible or defined

        if not os.path.exists(data_dir):
            print(f"Data directory '{data_dir}' does not exist. Skipping file cleanup.")
            return

        print(f"Checking for outdated SQLite data files in '{data_dir}'...")
        for filename in os.listdir(data_dir):
            file_path = os.path.join(data_dir, filename)
            if os.path.isfile(file_path):
                # Regex to find mm_dd_yyyy pattern in filename
                match = re.search(r'(\d{2}_\d{2}_\d{4})', filename)
                if match:
                    file_date_str = match.group(1)
                    # Only process .db files
                    if filename.endswith(".db"):
                        if file_date_str != today_date_str:
                            print(f"  Deleting outdated file: {filename} (Date: {file_date_str})")
                            try:
                                os.remove(file_path)
                            except OSError as e:
                                print(f"  Error deleting file {filename}: {e}")
                        #else:
                            #print(f"  Keeping current file: {filename} (Date: {file_date_str})")
                #else: # This else block is for files that do not match the date pattern
                    #print(f"  Skipping file (no date pattern or not .db): {filename}")
        print("Data file cleanup complete.")    

    #===========================================

    def serialize_weekly_data_to_sqlite(self):
        """
        Serializes the cached weekly data for all tickers into an SQLite database.
        Each ticker's data is stored in its own table named after the ticker symbol.

        Args:
            db_path (str): The path to the SQLite database file.
        """
        if not self._weeklydata_:
            print("No weekly data available to serialize.")
            return

        # Ensure the data directory exists
        data_dir = os.path.dirname(self.weekly_db_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)

        import sqlite3
        conn = None
        try: # Use self.weekly_db_path
            conn = sqlite3.connect(self.weekly_db_path)
            print(f"Serializing weekly data to {self.weekly_db_path}...")
            for ticker, df in self._weeklydata_:
                if not df.empty:
                    # Save DataFrame to SQLite table, replacing if exists
                    df.to_sql(ticker, conn, if_exists='replace', index=True)
                    print(f"  Saved data for {ticker}")
                else:
                    print(f"  Skipping empty data for {ticker}")
            print("Serialization complete.")
        except Exception as e:
            print(f"Error during serialization to SQLite: {e}")
        finally:
            if conn:
                conn.close()

    #===========================================

    def load_weekly_data_from_sqlite(self):
        """
        Loads weekly data for all tickers from an SQLite database.
        Each ticker's data is loaded from its own table named after the ticker symbol.

        Args:
            db_path (str): The path to the SQLite database file.
        
        Returns:
            list: A list of tuples, where each tuple contains (ticker, pd.DataFrame).
                  Returns an empty list if the database file does not exist or on error.
        """
        if not os.path.exists(self.weekly_db_path):
            print(f"Cached database not found at {self.weekly_db_path}. Cannot load weekly data.")
            return []
        
        import sqlite3
        conn = None
        try:
            conn = sqlite3.connect(self.weekly_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") # Use self.weekly_db_path
            tables = cursor.fetchall()
            
            loaded_data = []
            print(f"Loading weekly data from {self.weekly_db_path}...")
            for table_name_tuple in tables:
                ticker = table_name_tuple[0]
                df = pd.read_sql_query(f"SELECT * FROM '{ticker}'", conn, index_col='Date')
                df.index = pd.to_datetime(df.index, utc=True) # Ensure Date is datetime index
                loaded_data.append((ticker, df))
                print(f"  Loaded data for {ticker}")
            print("Loading complete.")
            self._weeklydata_ = loaded_data
            return loaded_data
        except Exception as e:
            print(f"Error during loading from SQLite: {e}")
            return []
        finally:
            if conn:
                conn.close()

    #===========================================

    def _initialize_tickers(self):
        """
        Loads tickers by calling the SP500TickerManager. The manager
        handles fetching from the source or loading from a local file.
        """
        try:
            dd = DataDownloader()
            # This single call handles all the logic of checking for the file,
            # fetching if needed, and loading the tickers.
            self._tickers_ = dd.get_ticker_list(filepath=self._ticker_filepath)
            print(len(self._tickers_))
            if self._tickers_ is None:
                # Ensure self.tickers is a list even on failure.
                self._tickers_ = []
        except Exception as e:
            print(f"Fatal: Could not initialize tickers. Error: {e}")
            self._tickers_ = []
    #===========================================

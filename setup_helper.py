import sqlite3
import pandas as pd
import os
from utility import get_date_mmddyyyy
from dataclasses import dataclass

@dataclass
class TradeParams:
    timestamp: str
    ticker: str
    timeframe: str
    entry: float 
    stop: float 
    tp: float 
    strategy: str

class SetupLogger:
    DB_PATH = os.path.join("reports", f"trade_setups_{get_date_mmddyyyy()}.db")

    @staticmethod
    def clear_sameday_setup_log():
        if os.path.exists(SetupLogger.DB_PATH):
            os.remove(SetupLogger.DB_PATH)

    @staticmethod
    def _create_tables():
        os.makedirs(os.path.dirname(SetupLogger.DB_PATH), exist_ok=True)
        conn = sqlite3.connect(SetupLogger.DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS buy_setups (
                timestamp TEXT,
                ticker TEXT,
                timeframe TEXT,
                entry REAL,
                stop REAL,
                tp REAL,
                strategy TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sell_setups (
                timestamp TEXT,
                ticker TEXT,
                timeframe TEXT,
                entry REAL,
                stop REAL,
                tp REAL,
                strategy TEXT
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def build_trade_params(row, ticker, strategy: str, buy: bool):
        if buy:
            entry = row['High']
            stop = row['Low']
            tp = entry + (entry - stop)
        else:
            entry = row['Low']
            stop = row['High']
            tp = entry - (stop - entry)
           
        # Extract timestamp from the row's index (which is a DatetimeIndex)
        timestamp_str = row.name.strftime('%Y-%m-%d %H:%M:%S') # Format as string

        setup_params = TradeParams(
            timestamp=timestamp_str,
            ticker=ticker, # Ticker needs to be passed from process_strat_F2_setups
            timeframe="Weekly",
            entry=round(entry, 4),
            stop=round(stop, 4),
            tp=round(tp, 4),
            strategy=strategy
        )
        return setup_params

    @staticmethod
    def log_buy_setup(setup: TradeParams):
        SetupLogger._create_tables() # Ensure tables exist
        conn = sqlite3.connect(SetupLogger.DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO buy_setups (timestamp, ticker, timeframe, entry, stop, tp, strategy)
            VALUES (?, ?, ?, ?, ?, ?, ?) 
        ''', (setup.timestamp, setup.ticker, setup.timeframe, setup.entry, setup.stop, setup.tp, setup.strategy))
        conn.commit()
        conn.close()

    @staticmethod
    def log_sell_setup(setup: TradeParams):
        SetupLogger._create_tables() # Ensure tables exist
        conn = sqlite3.connect(SetupLogger.DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sell_setups (timestamp, ticker, timeframe, entry, stop, tp, strategy)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (setup.timestamp, setup.ticker, setup.timeframe, setup.entry, setup.stop, setup.tp, setup.strategy))
        conn.commit()
        conn.close()

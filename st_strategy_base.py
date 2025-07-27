from abc import ABC, abstractmethod
import pandas as pd

import time
from functools import wraps
from data_manager import DataManager
from setup_helper import TradeParams

#===========================================

def timeit(method):
    @wraps(method)
    def timed(*args, **kwargs):
        start_time = time.time()
        result = method(*args, **kwargs)
        elapsed = time.time() - start_time
        print(f"[{method.__qualname__}] executed in {elapsed:.4f}s")
        return result
    return timed

#===========================================

class BaseStrategy(ABC):
    _instances = {}

    def __new__(cls):
        if cls not in cls._instances:
            cls._instances[cls] = super(BaseStrategy, cls).__new__(cls)
        return cls._instances[cls]

    def __init__(self, *args, **kwargs):
        # Only initialize once per singleton instance
        if not hasattr(self, 'dm'):
            self.dm = kwargs.get('dm', DataManager())

    @timeit
    @abstractmethod
    def process_data(self):
        print("impliment override")

    @timeit
    @abstractmethod
    def generate_reports(self):
        print("impliment override")

    @timeit
    @abstractmethod
    def log_buy_setup(self, tparams: TradeParams):
        print("impliment override")

    @timeit
    @abstractmethod
    def log_sell_setup(self, tparams: TradeParams):
        print("impliment override")

    def __str__(self):
        return self.__class__.__name__

    @timeit
    def fetch_data_collection(self):
        """
        Fetches the data collection for the strategy.
        """
        
        collection = self.dm.get_weekly_data()
        return collection 
#===========================================

# Assuming downloader.py is in the same directory or in the python path
#from thestrat import StratProcessor
from data_manager import DataManager
from st_strategy_factory import StrategyFactory
from setup_helper import SetupLogger

#===========================================

class Context:
    """
    A context class to hold application-wide session data.

    This class is intended to be instantiated once as a 'session' object
    that can be imported and used by other parts of the application.
    A class to hold application-wide session data.

    This class is intended to be instantiated once as a 'session' object
    that can be imported and used by other parts of the application.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Context, cls).__new__(cls)
        return cls._instance

    #===========================================

    def __init__(self):
        """
        Initializes the context by loading the list of S&P 500 tickers.

        If the ticker file specified by `ticker_filepath` does not exist,
        it will attempt to fetch the tickers from the source and create it.

        Args:
            ticker_filepath (str): The path to the JSON file containing tickers.
        """
        #self.dm = DataManager()
        self.strat_factory = StrategyFactory()
        SetupLogger.clear_sameday_setup_log()


    #===========================================


#===========================================
# globals.
# Instantiate the Context class as a session object.
# Other modules in the project can now `from launcher import session`
# to get access to the application context.
session = Context()

#===========================================    


#===========================================

if __name__ == "__main__":
    import time
    start_time = time.perf_counter()

    try:
        print("--- SYJ_TA Launcher ---")
        strat = session.strat_factory.get_instance_by_description('parabolic')
        strat.process_data()
        
        """
        strats_list = session.strat_factory.get_all_instances()

        for strat in strats_list:
            print(strat)
            strat.process_data()
            #break # remove this in final edition
        """

    except Exception as ex:
        print(ex)
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    print(f"\nTotal execution time: {duration:.2f} seconds.")
    print("\n--- Launcher Finished ---")
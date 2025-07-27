from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas as pd
import os
import utility
from data_manager import DataManager
from setup_helper import SetupLogger, TradeParams
from st_strategy_base import BaseStrategy

#===========================================

class Parabolic(BaseStrategy):
    """
    Processes and visualizes trading strategies based on the S&P 500 data.
    """
    
    def __init__(self):
        super().__init__()
        print("Initializing Parabolic Strategy")

    #===========================================

    def __str__(self):
        return "parabolic"

    #===========================================

    def process_data(self):
        basedata = self.fetch_data_collection()
        print("getting close data")
        back_date = pd.to_datetime(utility.get_back_date(10, 0, 0))
        #close_data = self.dm.get_close_on_date(back_date)

        high_data = self.dm.get_yearly_high(back_date.year)

        print(f"entries on {back_date}: {len(high_data)}")
        #print(close_data)
        beaten = []
        fallen = []
        for ticker, df in basedata:
            #print(ticker)
            hist_high = next((v for t, v in high_data if t == ticker), None)            
            if hist_high:
                last_close = df.iloc[-1]['Close']
                last_close = float(last_close)
                if last_close < hist_high:
                    pval = ((hist_high-last_close)/hist_high)*100
                    fallen.append((ticker, pval))
                #print(f"{ticker} last close: {last_close}, historical close: {hist_close}")
                if last_close < (float(hist_high) * 0.20):
                    beaten.append((ticker, df))
                    print(f"{ticker} is beaten down")
                    with open(os.path.join("reports", "sp500", "beaten_down_stocks.txt"), "a+") as f:
                        f.writelines([f"scanned on {utility.get_date_mmddyyyy()}: {ticker}, historic high ({back_date.year}): {round(hist_high, 4)}, last close: {round(last_close, 4)}\n"])

        print(f"Total beaten down stocks: {len(beaten)}")
        print([t for t, d in beaten])



    #===========================================

    def generate_reports(self):
        pass

    #===========================================

    def log_buy_setup(self, tparams):
        pass

    #===========================================
    
    def log_sell_setup(self, tparams):
        pass

    #===========================================

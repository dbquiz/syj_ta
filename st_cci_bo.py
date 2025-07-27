import matplotlib.pyplot as plt
import mplfinance as mpf
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import numpy as np
from st_strategy_base import BaseStrategy
from setup_helper import TradeParams
import utility
from setup_helper import SetupLogger

#===========================================
# CCI Breakout Strategy
"""
This strategy identifies CCI breakouts based on a specified threshold.
It generates buy and sell signals based on the CCI values crossing above or below the thresholds.
"""
class CCIBO(BaseStrategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cci_span = 34
        self.cci_up_threshold = 100
        self.cci_down_threshold = -100

    #===========================================

    def __str__(self):
        return "CCIBO"
    
    #============================================

    def process_data(self):
        # Implement the logic to process the data for CCI BO strategy
        print(self.__str__())
        basedata = self.fetch_data_collection()
        with PdfPages(f'reports/SP500_Weekly_CCI_BO_buy_setups_{utility.get_date_mmddyyyy()}.pdf') as buy_pdf, \
             PdfPages(f'reports/SP500_Weekly_CCI_BO_sell_setups_{utility.get_date_mmddyyyy()}.pdf') as sell_pdf:
            for ticker, df in basedata:
                df = self._calculate_cci_params(df)
                #gather last 2 rows
                dftail = df.tail(2)

                last_row = dftail.iloc[-1]
                if dftail.iloc[-1]['Mode'] == 'BUY' and dftail.iloc[-2]['Mode'] != 'BUY':
                    tparams = SetupLogger.build_trade_params(last_row, ticker, 'CCIBO', buy=True)
                    self.log_buy_setup(tparams)

                    img = self._plot_cci_chart(ticker, 'Buy', df)
                    buy_pdf.savefig(img)
                    plt.close(img)
                elif dftail.iloc[-1]['Mode'] == 'SELL' and dftail.iloc[-2]['Mode'] != 'SELL':
                    tparams = SetupLogger.build_trade_params(last_row, ticker, 'CCIBO', buy=False)
                    self.log_sell_setup(tparams)

                    img = self._plot_cci_chart(ticker, 'Sell', df)
                    sell_pdf.savefig(img)
                    plt.close(img)

    #===========================================

    def _calculate_cci_params(self, df: pd.DataFrame):
        # Implement the logic to calculate CCI parameters
        #print("Calculating CCI parameters")
        df['Typical Price'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['SMA_CCI'] = df['Typical Price'].rolling(window=self.cci_span).mean()
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['Mean Deviation'] = df['Typical Price'].rolling(window=self.cci_span).apply(lambda x: (x - x.mean()).abs().mean())
        df['CCI'] = (df['Typical Price'] - df['SMA_CCI']) / (0.015 * df['Mean Deviation'])
        conditions = [
            df['CCI'] > self.cci_up_threshold,
            df['CCI'] < self.cci_down_threshold
        ]
        choices = ['BUY', 'SELL']
        df['Mode'] = np.select(conditions, choices, default='HOLD')
        df = df.dropna(subset=['EMA20', 'CCI', 'Mode'])
        return df
    
    #===========================================

    def _plot_cci_chart(self, ticker: str, setup: str, df: pd.DataFrame):
        plot_df = df[['Open', 'High', 'Low', 'Close', 'EMA20', 'CCI']]
        apds = [
            mpf.make_addplot(plot_df['EMA20'], color='blue', width=1),
            mpf.make_addplot(plot_df['CCI'], panel=1, color='orange', ylabel='CCI'),
        ]
        title = f"{ticker} weekly CCI BO setup. Setup: {setup} CCI: {plot_df['CCI'].iloc[-1]:.2f}"
        
        img = mpf.plot(plot_df, type='candle', addplot=apds, title=title, style='yahoo', returnfig=True)
        return img[0]
    
    #===========================================
    
    def generate_reports(self):
        # Implement the logic to generate reports for CCI BO strategy
        print("Generating reports for CCI BO strategy")
    
    #===========================================

    def log_buy_setup(self, tparams: TradeParams):
        # Implement the logic to log buy setup for CCI BO strategy
        print(f"Buy setup {tparams.ticker}")        
        SetupLogger.log_buy_setup(tparams)

    #===========================================
    
    def log_sell_setup(self, tparams: TradeParams):
        # Implement the logic to log sell setup for CCI BO strategy
        print(f"Sell setup {tparams.ticker}")
        SetupLogger.log_sell_setup(tparams)

#===========================================
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from matplotlib.backends.backend_pdf import PdfPages
import utility
from st_strategy_base import BaseStrategy
from setup_helper import *

#===========================================
class ZIndex(BaseStrategy):
    def __str__(self):
        return "ZIndex"

    def __init__(self):
        super().__init__()
        self.ema_span = 20
        self.z_threshold = 2

    def process_data(self, basedata:list):
        with PdfPages(f'reports/SP500_Weekly_ZIndex_buy_setups_{utility.get_date_mmddyyyy()}.pdf') as buy_pdf, \
             PdfPages(f'reports/SP500_Weekly_ZIndex_sell_setups_{utility.get_date_mmddyyyy()}.pdf') as sell_pdf:
            for ticker, df in basedata:
                df = self._calculate_zi_params(df)
                df = self._detect_reversals(df)
                last_row = df.iloc[-1]
                if last_row['Bottom']:
                    tparams = SetupLogger.build_trade_params(last_row, ticker, 'ZIndex', buy = True)
                    self.log_buy_setup(tparams)

                    img = self._plot_zi_chart(ticker, 'Buy', df)
                    buy_pdf.savefig(img)
                    plt.close(img)
                elif last_row['Top']:
                    tparams = SetupLogger.build_trade_params(last_row, ticker, 'ZIndex', buy = False)
                    self.log_sell_setup(tparams)

                    img = self._plot_zi_chart(ticker, 'Sell', df)
                    sell_pdf.savefig(img)
                    plt.close(img)

    def generate_reports(self):
        return super().generate_reports()

    def log_buy_setup(self, tparams: TradeParams):
        SetupLogger.log_buy_setup(tparams)

    def log_sell_setup(self, tparams: TradeParams):
        SetupLogger.log_sell_setup(tparams)

    #===========================================

    def _plot_zi_chart(self, ticker: str, setup: str, df: pd.DataFrame):
        plot_df = df[['Open', 'High', 'Low', 'Close', 'EMA5', 'EMA20', 'Upper', 'Lower', 'Top', 'Bottom']]
        apds = [
            mpf.make_addplot(plot_df['EMA5'], color='blue', width=1),
            mpf.make_addplot(plot_df['EMA20'], color='blue', width=1),
            mpf.make_addplot(plot_df['Upper'], color='gray', linestyle='dotted', width=0.7),
            mpf.make_addplot(plot_df['Lower'], color='gray', linestyle='dotted', width=0.7),
        ]
        title=f"{ticker} weekly ZIndex reversal. Setup:{setup}"
        #plot without actually rendering on screen
        fig, axlist = mpf.plot(
            plot_df,
            type='candle',
            style='charles',
            title = title,
            ylabel='Price',
            volume=False,
            addplot=apds,
            returnfig=True,
            figratio=(14,7),
            figscale=1.2,
            tight_layout=False,
            xrotation=15
        )
        
        ax = axlist[0] # price axis
        x_vals = list(range(len(plot_df)))
        dates = plot_df.index

        # Plot 'T' and 'B' as text labels at correct positions
        for i, (idx, row) in enumerate(plot_df.iterrows()):
            if row['Top']:
                ax.text(x_vals[i], row['High'] * 1.01, 'T', color='red',
                        fontsize=10, ha='center', va='bottom', fontweight='bold')
            if row['Bottom']:
                ax.text(x_vals[i], row['Low'] * 0.99, 'B', color='green',
                        fontsize=10, ha='center', va='top', fontweight='bold')

        return fig
    
    #===========================================

    def _detect_reversals(self, df: pd.DataFrame):
        #print('detecting reversal')
        df['Top'] = (df['High'] > df['Upper']) & (df['Close'] < df['EMA5'])
        df['Bottom'] = (df['Low'] < df['Lower']) & (df['Close'] > df['EMA5'])
        return df

    #===========================================
    
    def _calculate_zi_params(self, df: pd.DataFrame):
        df = df.copy()
        df['EMA5'] = df['Close'].ewm(span=5, adjust=False).mean()       
        df['EMA20'] = df['Close'].ewm(span=self.ema_span, adjust=False).mean() 

        df.dropna(inplace=True)
        df['Rolling_Std'] = df['Close'].rolling(window=self.ema_span).std()
        df['Upper'] = df['EMA20'] + (df['Rolling_Std'] * self.z_threshold)
        df['Lower'] = df['EMA20'] - (df['Rolling_Std'] * self.z_threshold)

        return df

#===========================================
import pandas as pd

import matplotlib.pyplot as plt
import mplfinance as mpf
from matplotlib.backends.backend_pdf import PdfPages
from setup_helper import TradeParams
from setup_helper import SetupLogger
import utility
from st_strategy_base import BaseStrategy
#===========================================

class TheStrat(BaseStrategy):
    def __init__(self):
        super().__init__()
        

    def __str__(self):
        return "TheStrat"

    def process_data(self):
        basedata = self.fetch_data_collection()
        with PdfPages(f'reports/SP500_Weekly_F2_buy_setups_{utility.get_date_mmddyyyy()}.pdf') as buy_pdf, \
             PdfPages(f'reports/SP500_Weekly_F2_sell_setups_{utility.get_date_mmddyyyy()}.pdf') as sell_pdf:
            for ticker, data in basedata:
                df = data.copy()
                df = self.assign_strat_codes(df)
                
                last_wick_label = df['Wick_Label'].iloc[-1]
                last_row = df.iloc[-1]
                if last_row['Wick_Label'] == 'f2d': # f2d is a buy setup
                    # Pass ticker to save_buy_setup
                    tparams = SetupLogger.build_trade_params(last_row, ticker, 'StratF2D', buy = True)
                    self.log_buy_setup(tparams)
                    print(f'Buy setup: {ticker}')
                    img = StratProcessor.plot_f2_setups(ticker, 'Buy', df)
                    buy_pdf.savefig(img)
                    plt.close(img)
                elif last_row['Wick_Label'] == 'f2u': # f2u is a sell setup
                    # Pass ticker to save_sell_setup
                    tparams = SetupLogger.build_trade_params(last_row, ticker, 'StratF2U', buy = False)
                    self.log_sell_setup(tparams)
                    print(f'Sell setup: {ticker}')
                    img = StratProcessor.plot_f2_setups(ticker, 'Sell', df)
                    sell_pdf.savefig(img)
                    plt.close(img)


    def assign_strat_codes(self, df: pd.DataFrame):
        highs = df['High']
        lows = df['Low']

        df['Range'] = highs - lows
        labels = []

        for i in range(len(df)):
            if i == 0:
                labels.append(None)
                continue

            hi, lo = highs.iloc[i], lows.iloc[i]
            hi_prev, lo_prev = highs.iloc[i-1], lows.iloc[i-1]

            if hi < hi_prev and lo > lo_prev:
                labels.append('1')
            elif hi > hi_prev and lo < lo_prev:
                labels.append('3')
            elif hi > hi_prev and lo >= lo_prev:
                labels.append('2u')
            elif lo < lo_prev and hi <= hi_prev:
                labels.append('2d')
            else:
                labels.append(None)

        df['BarType'] = labels

        # Build last 3 labels as concatenated string
        sequences = []
        for i in range(len(df)):
            if i < 3:
                sequences.append(None)
            else:
                seq = df['BarType'].iloc[i-2:i+1].tolist()
                if None in seq:
                    sequences.append(None)
                else:
                    sequences.append('_'.join(seq))
        df['StratSequence'] = sequences

        df = self._F2Setup_(df)
        df = self._combine_range_and_wick_labels_(df)
        
        return df
    
    #================================================

    def _combine_range_and_wick_labels_(self, df: pd.DataFrame):
        def combine(row):
            r, w = row['BarType'], row['Wick_Label']
            if pd.notna(r) and r != '' and pd.notna(w) and w != '':
                return f"{w}" # for wick label, it already includes bar_type info. so no need to add r.
            elif pd.notna(r) and r != '':
                return r
            elif pd.notna(w) and w != '':
                return w
            else:
                return None
        df['Combo_Label'] = df.apply(combine, axis=1)
        return df

    #================================================

    def _F2Setup_(self, df: pd.DataFrame):
        o = df['Open']
        h = df['High']
        l = df['Low']
        c = df['Close']

        upper_wick = h - o.combine(c, max)
        lower_wick = o.combine(c, min) - l
        body = abs(c - o)
        candle_height = h - l

        df['Wick_Label'] = ''

        # Condition: body < 0.5 * height
        small_body_mask = body < (0.5 * candle_height)

        df.loc[(lower_wick > upper_wick) & small_body_mask, 'Wick_Label'] = 'f2d'
        df.loc[(upper_wick > lower_wick) & small_body_mask, 'Wick_Label'] = 'f2u'

        return df

    #================================================

    def generate_reports(self):
        return super().generate_reports()

    def log_buy_setup(self, tparams: TradeParams):
        SetupLogger.log_buy_setup(tparams)

    def log_sell_setup(self, tparams: TradeParams):
        SetupLogger.log_sell_setup(tparams)


#===========================================


class StratProcessor:
    """
        This class deals with TheStrat strategy which is simple and works with candle types.
        t1 - inside bar
        t3 - outside bar
        t2u - outside bar only on upside
        t2d - outside bar only on downside
        f2u - makes t2u but marks large wick, failing to close strong
        f2d - makes t2d but marks large wick, failing to close strong
    """
    #===========================================
    
    @staticmethod
    def plot_f2_setups(ticker: str, setup: str, df: pd.DataFrame):
        plot_df = df[['Open', 'High', 'Low', 'Close']]
        title = f"{ticker} - weekly f2 setups. latest - {df['Wick_Label'].iloc[-1]} | {setup}."
        # Create the mplfinance figure and axes
        fig, axes = mpf.plot(
            plot_df,
            type='candle',
            style='charles',
            title=title,
            ylabel='Price',
            volume=False,
            returnfig=True,
            figscale=1.2,
            figratio=(16, 9),
            xrotation=15,
            tight_layout=False
        )
        fig.subplots_adjust(right=0.96, left=0.08, top=0.93, bottom=0.15)
        ax = axes[0]

        # Use internal mplfinance x-values for annotations
        x_positions = range(len(df))
        for x, (_, row) in zip(x_positions, df.iterrows()):
            label = row.get('Wick_Label', '')
            if label:
                y = row['High'] + (row['High'] - row['Low']) * 0.04
                ax.text(
                    x, y,
                    label,
                    fontsize=4,
                    color='green' if 'f2d' in label else 'red',
                    rotation=0,
                    ha='center',
                    va='bottom',
                    clip_on=True
                )

        return fig

    
    #===========================================
        
    @staticmethod
    def plot_with_wick_labels(ticker: str, df: pd.DataFrame):
        plot_df = df[['Open', 'High', 'Low', 'Close']]
        title = f"{ticker} - weekly strat labels. combo - {df['StratSequence'].iloc[-1]}"

        # Create the mplfinance figure and axes
        fig, axes = mpf.plot(
            plot_df,
            type='candle',
            style='charles',
            title=title,
            ylabel='Price',
            volume=False,
            returnfig=True,
            figscale=1.2,
            figratio=(16, 9),
            xrotation=15,
            tight_layout=False
        )
        ax = axes[0]  # Price axis

        # Use position index for x and adjust y carefully
        for i, (timestamp, row) in enumerate(df.iterrows()):
            label = row.get('Combo_Label', None)
            if label:
                y = row['High'] + (row['High'] - row['Low']) * 0.05  # ~5% above high
                ax.text(
                    i, y,
                    label,
                    fontsize=4,
                    color='blue',
                    rotation=0,
                    ha='center',
                    va='bottom',
                    clip_on=True
                )

        return fig
    
    #===========================================
    @staticmethod
    def process_strat_all(basedata: list):
        with PdfPages(f'reports/SP500_strat_reports_{utility.get_date_mmddyyyy()}.pdf') as pdf:
            for ticker, data in basedata:
                df = data.copy()
                #print(df.tail(10))
                df = StratProcessor.assign_strat_codes(df)
                #print(df.tail(10))
                img = StratProcessor.plot_with_wick_labels(ticker, df)
                pdf.savefig(img)
                plt.close(img)

    
    #===========================================

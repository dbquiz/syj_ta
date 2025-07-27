import datetime
import pandas as pd

def get_date_mmddyyyy():
    return datetime.datetime.now().strftime("%m_%d_%Y")

def get_back_date(years=0, months=0, days=0):
    """
    Returns a date string for a date that is 'years' years back from today.
    """
    back_date = datetime.datetime.now() - datetime.timedelta(days= (years * 365 + months*30 + days))

    # If the date is a weekend (Saturday=5, Sunday=6), go back by 2 days to get Friday
    if back_date.weekday() == 5:  # Saturday
        back_date = back_date - pd.Timedelta(days=2)
    elif back_date.weekday() == 6:  # Sunday
        back_date = back_date - pd.Timedelta(days=3)
        
    date_str = back_date.strftime('%Y-%m-%d')
    print(f"Back date calculated: {date_str}, day of week: {back_date.strftime('%A')} ")
    return date_str
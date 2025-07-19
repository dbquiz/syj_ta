import datetime

def get_date_mmddyyyy():
    return datetime.datetime.now().strftime("%m_%d_%Y")

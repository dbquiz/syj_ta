1. use venv
command - python -m venv venv

2. activate venv
command - venv/Scripts/Activate

3. install packages
command - pip install mplfinance yfinance requests

4. run launcher.py
command - python launcher.py

5. folders -
current folder has codebase all files in same level
data: contains data to download historic data and cache.
reports: generated pdf files are placed in here.

6. How to add new strategy
a. create subclass of BaseStrategy
b. implement all apis - refer other classes for input and output paths
c. give one word name in __str__ 
d. modify strategy_factory to give instance of new strategy.

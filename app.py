import os
import requests
import re
from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.layouts import column
from bokeh.models import CustomJS, TextInput
from bokeh.models.tools import HoverTool
import pandas as pd


# Read in AlphaVantage API key
API_KEY = os.environ.get('API_KEY')

# Set up API query
ticker = 'AAPL'
API = 'TIME_SERIES_DAILY_ADJUSTED'
url = 'https://www.alphavantage.co/query?function={}&symbol={}&apikey={}'.format(API, ticker, API_KEY)

# Request data
response = requests.get(url)
stock_tick = response.json()

# Convert json response to data frame
info_keys = list(stock_tick.keys())
stock_df = pd.DataFrame.from_dict(stock_tick[info_keys[1]], orient='index')
stock_df = stock_df.rename(columns=lambda x: re.sub('^.\.\s', '', x))
stock_df.index = pd.to_datetime(stock_df.index, format='%Y-%m-%d')


# Plot with bokeh
output_file('stock_ticker.html')
p = figure(plot_height=400,
           plot_width=800,
           x_axis_label='Date',
           x_axis_type='datetime',
           y_axis_label='Adjusted closing price',
           title='{} adjusted closing prices'.format(ticker))
p.line('index', 'close', source=stock_df, line_color='black', line_width=2)
p.add_tools(HoverTool(tooltips=[
    ("Stock", ticker),
    ("Date", "$x{%F}"),
    ("Price", "$y"),
], formatters={'$x': 'datetime'}))
curdoc().add_root(column(p))

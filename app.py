import os
import requests
import re
import pandas as pd
from bokeh.models import ColumnDataSource, Select, Slider
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models.callbacks import CustomJS
from bokeh.models.tools import HoverTool
from flask import Flask, render_template
from dotenv import load_dotenv


app = Flask(__name__)

@app.route('/')
def index():

    # Read in AlphaVantage API key
    load_dotenv()
    API_KEY = os.environ['API_KEY']

    def selectedTicker(value='AAPL'):
        ticker = value
        API = 'TIME_SERIES_DAILY_ADJUSTED'
        url = 'https://www.alphavantage.co/query?function={}&symbol={}&apikey={}'.format(API, ticker, API_KEY)
        response = requests.get(url)
        stock_tick = response.json()

        # Convert json response to data frame
        info_keys = list(stock_tick.keys())
        stock_df = pd.DataFrame.from_dict(stock_tick[info_keys[1]], orient='index')
        stock_df = stock_df.rename(columns=lambda x: re.sub('^.\.\s', '', x))
        stock_df.index = pd.to_datetime(stock_df.index, format='%Y-%m-%d')
        return ticker, stock_df

    source = ColumnDataSource()

    # callback = CustomJS(args=dict(source=source, controls=controls), code="""
    #     if (!window.full_data_save) {
    #         window.full_data_save = JSON.parse(JSON.stringify(source.data));
    #     }
    #     var full_data = window.full_data_save;
    #     var full_data_length = full_data.x.length;
    #     var new_data = { x: [], y: [], color: [], title: [], released: [], imdbvotes: [] }
    #     for (var i = 0; i < full_data_length; i++) {
    #         if (full_data.imdbvotes[i] === null || full_data.released[i] === null || full_data.genre[i] === null)
    #             continue;
    #         if (
    #             full_data.imdbvotes[i] > controls.reviews.value &&
    #             Number(full_data.released[i].slice(-4)) >= controls.min_year.value &&
    #             Number(full_data.released[i].slice(-4)) <= controls.max_year.value &&
    #             (controls.genre.value === 'All' || full_data.genre[i].split(",").some(ele => ele.trim() === controls.genre.value))
    #         ) {
    #             Object.keys(new_data).forEach(key => new_data[key].push(full_data[key][i]));
    #         }
    #     }
    #     source.data = new_data;
    #     source.change.emit();
    # """)

    ticker, stock_prices = selectedTicker()

    fig = figure(plot_height=400,
           plot_width=800,
           x_axis_label='Date',
           x_axis_type='datetime',
           y_axis_label='Adjusted close',
           title='{} adjusted closing prices'.format(ticker))
    fig.line(x="x", y="y", source=source, line_color="black", line_width=2)
    fig.add_tools(HoverTool(tooltips=[
        ("Stock", ticker),
        ("Date", "$x{%F}"),
        ("Price", "$y"),
    ], formatters={'$x': 'datetime'}))

    source.data = dict(
        x=stock_prices.index,
        y=stock_prices.close,
    )

    script, div = components(fig)
    return render_template(
        'index.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
    ).encode(encoding='UTF-8')

if __name__ == "__main__":
    app.run(debug=True)



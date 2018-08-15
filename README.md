# STITAP Stock Screener V1.1.0

STITAP stock screener is a free, open-source program which screens all 30 companies of the Straits Times Index using common technical indicators.

It uses a [python interface](https://github.com/RomelTorres/alpha_vantage) to retrieve data from [Alpha Vantage](https://www.alphavantage.co/), which provides a free API for both historical and real-time financial data.

Get your free API key [here](https://www.alphavantage.co/support/#api-key).

## How it works

For a gentle introduction to STITAP and its functionalities, you can refer to [this article](http://www.leeweimin.com/2018/07/19/programming-your-free-singapore-stock-screener/).

Simply put, STITAP pulls data from AlphaVantage through its API before performing calculations and storing the results in csv files. The program is run using the python shell.

## Installation

### For normal users

If you do not already have Python IDLE installed, you can get it [here](https://www.python.org/getit/).

Install [Pandas](https://pandas.pydata.org/getpandas.html) and [Numpy](https://sourceforge.net/projects/numpy/), or just download [Anaconda](https://www.anaconda.com/download/).

Clone the repository by clicking the green button on the top right corner of the page.

Go to the folder STI_Stock_Screener -> alpha_vantage. Run the file run.py.

## Running STITAP

Get your free AlphaVantage API key [here](https://www.alphavantage.co/support/#api-key).

In run.py, set the key argument to your API key value in the Initializer class:

```python
class Initializer(ABC):
	"""Abstract base class for initializing the program
	"""
	def __init__(self, timeframe="daily"):
		"""Initializes the class by creating a new TimeSeries object

		Keyword Arguments:
			timeframe: timeframe for backtest. Supported values are "daily", "weekly" and "monthly" (default "daily")
		"""
		self._ts = TimeSeries(key="", output_format="pandas") # <--- SET API KEY HERE
		self._timeframe = timeframe
```

Run run.py. Enjoy!

### Adjust API call frequency

*Do note that AlphaVantage limits the frequency of API calls*

You can adjust the frequency of API calls in the \_loop() method in the Initializer class:

```python
def _loop(self):
		"""Loops over each stock, using the _fetch_store() method to fetch and store each stock's data
		"""
		for stock_name, stock_ticker in sti_stocks.items():
			time.sleep(0.1)
			print (f"LOADING: {stock_name} {stock_ticker}", end="\n"*2)
			stock_name_no_spaces = stock_name.replace(" ", "_")
			time.sleep(60) # <--- Adjust the duration (No. of seconds) of waiting time between each API call here
			self._fetch_store(stock_name_no_spaces, stock_ticker, self._timeframe)
```

## Features

### General screen

* Top 5 stocks with highest/lowest price/volume change

### Technical indicators

* Moving Average Convergence / Divergence (MACD)
* Relative Strength Index (RSI)
* Stochastic Relative Strength Index (StochRSI)

You can refer to examples [here](http://www.leeweimin.com/2018/07/19/programming-your-free-singapore-stock-screener/).

## Contributing

Contributions are always welcome.

If you can find a way to improve this project, do send a pull request.

## FAQ

* **My program crashed shortly after running run.py. How do I fix this?**

  * The program may have exceeded the API call frequency limit. You can either restart the program after waiting a few minutes or adjust the frequency of API calls (please refer to the "adjust API call frequency" section).

* **The technical indicator values are not exactly accurate. Why?**

	 * The timeframes used in the program are estimated and do not take into account public holidays. We will fix this in future updates. (*This has been fixed in V1.1.0*)

## Contact

You can get in touch with me through my [website](http://www.leeweimin.com/contact/).

## TODOs:
* Improve accuracy of technical indicators (*Done*)
* Reduce code repetition (*Done*)
* Add more technical indicators
* Set up a database and server
* Introduce backtesting

## Star if you like it.
If you enjoyed using this, do show your support by starring it!

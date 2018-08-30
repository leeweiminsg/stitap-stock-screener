from abc import ABC, abstractmethod
import time
from datetime import datetime
import json
import decimal
from pprint import pprint

import pandas as pd
import numpy as np

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from stitap_screens import TopPricePctChangeScreen, TopVolumePctChangeScreen
from stitap_ta_menu import TechnicalAnalysisMenu
from stitap_ta_screens import MACDScreener, RSIScreener, StochRSIScreener


sg_public_holidays_dates = ["2018-01-01", "2018-02-16", "2018-03-30", "2018-05-01", "2018-05-29",
					  		"2018-06-15", "2018-08-09", "2018-08-22", "2018-11-06", "2018-12-25"]

sti_stocks = {"CityDev":"C09.SI", "DBS":"D05.SI", "UOL":"U14.SI", "SingTel":"Z74.SI", "UOB":"U11.SI",
				"Keppel Corp":"BN4.SI", "CapitaLand":"C31.SI", "OCBC Bank":"O39.SI", "Genting Sing":"G13.SI", "Venture":"V03.SI",
				"CapitaMall Trust":"C38U.SI", "YZJ Shipbldg SGD":"BS6.SI", "CapitaCom Trust":"C61U.SI", "Ascendas Reit":"A17U.SI", "ComfortDelGro":"C52.SI",
				"SIA":"C6L.SI", "Jardine C&C":"C07.SI", "SPH":"T39.SI", "SGX":"S68.SI", "ThaiBev":"Y92.SI",
				"ST Engineering":"S63.SI", "Sembcorp Ind":"U96.SI", "Wilmar Intl":"F34.SI", "StarHub":"CC3.SI", "SATS":"S58.SI",
				"HongkongLand USD":"H78.SI", "JSH USD":"J37.SI", "JMH USD":"J36.SI", "HPH Trust USD":"NS8U.SI", "Golden Agri-Res":"E5H.SI"}


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

	@property
	def timeframe(self):
		return self._timeframe

	@timeframe.setter
	def timeframe(self, timeframe):
		self._timeframe = timeframe

	def _start(self):
		"""Prints the introduction to the program
		"""
		print("-----Straits Times Index Technical Analysis Project: STITAP-----", end="\n"*3)
		time.sleep(0.1)
		print("-----V1.1-----", end="\n"*3)
		time.sleep(0.1)

	def _loop(self):
		"""Loops over each stock, using the _fetch_store() method to fetch and store each stock's data
		"""
		for stock_name, stock_ticker in sti_stocks.items():
			time.sleep(0.1)
			print (f"LOADING: {stock_name} {stock_ticker}", end="\n"*2)
			stock_name_no_spaces = stock_name.replace(" ", "_")
			time.sleep(60) # <--- Adjust the duration (No. of seconds) of waiting time between each API call here
			self._fetch_store(stock_name_no_spaces, stock_ticker, self._timeframe)

	@abstractmethod		
	def _fetch_store(self, stock_name_no_spaces, stock_ticker, timeframe="daily"):
		"""Fetches and stores a stock's data

		Positional Arguments:
			stock_name_no_spaces: stock's name (without spaces)
			stock_ticker: stock's ticker

		Keyword Arguments:
			timeframe: timeframe for screener. Supported values are "daily", "weekly" and "monthly" (default "daily")
		"""
		pass

	def _end(self):
		"""Prints the end of the initializing process
		"""
		print("INITIALIZED: ALL 30 STI STOCK DATA LOADED AND SAVED", end="\n"*2)
		print("-"*20, end="\n"*2)

	def initialize(self):
		"""Initializes program
		"""
		self._start()
		self._loop()
		self._end()


class ScreenInitializer(Initializer):
	def __init__(self, timeframe="daily"):
		"""Initializes the screener

		Keyword Arguments:
			timeframe: timeframe for screener. Supported values are "daily", "weekly" and "monthly" (default "daily")
		"""
		super().__init__(timeframe)

	def _fetch_store(self, stock_name_no_spaces, stock_ticker, timeframe="daily"):
		"""Fetches and stores a stock's data

		Positional Arguments:
			stock_name_no_spaces: stock's name (without spaces)
			stock_ticker: stock's ticker

		Keyword Arguments:
			timeframe: timeframe for screener. Supported values are "daily", "weekly" and "monthly" (default "daily")
		"""
		if timeframe == "daily":
			data, _ = self._ts.get_daily_adjusted(symbol=stock_ticker)
		elif timeframe == "weekly":
			data, _ = self._ts.get_weekly_adjusted(symbol=stock_ticker)
		elif timeframe == "monthly":
			data, _ = self._ts.get_monthly_adjusted(symbol=stock_ticker)

		# Sorts the data dataframe in order of recency (latest date on top)
		data.sort_index(ascending=False, inplace=True)
		# Stores the data dataframe as csv in sti_stock_data/original_data
		data.to_csv(f"sti_stock_data/original_data/{timeframe}/{stock_name_no_spaces}.csv", mode="w")


class BacktestInitializer(Initializer):
	def __init__(self, timeframe="daily"):
		"""Initializes the backtest

		Keyword Arguments:
			timeframe: timeframe for backtest. Supported values are "daily", "weekly" and "monthly" (default "daily")
		"""
		super().__init__(timeframe)

	def _fetch_store(self, stock_name_no_spaces, stock_ticker, timeframe="daily"):
		"""Fetches and stores a stock's data

		Positional Arguments:
			stock_name_no_spaces: stock's name (without spaces)
			stock_ticker: stock's ticker

		Keyword Arguments:
			timeframe: timeframe for screener. Supported values are "daily", "weekly" and "monthly" (default "daily")
		"""
		if timeframe == "daily":
			data, _ = self._ts.get_daily_adjusted(symbol=stock_ticker, outputsize="full")
		elif timeframe == "weekly":
			data, _ = self._ts.get_weekly_adjusted(symbol=stock_ticker)
		elif timeframe == "monthly":
			data, _ = self._ts.get_monthly_adjusted(symbol=stock_ticker)

		# Sorts the data dataframe in order of recency (latest date on top)
		data.sort_index(ascending=False, inplace=True)
		# Stores the data dataframe as csv in sti_stock_data/backtest_data
		data.to_csv(f"sti_stock_data/backtest_data/{timeframe}/{stock_name_no_spaces}.csv", mode = "w")


class Wrangler():
	"""Wrangles data for screener
	"""
	def __init__(self):
		"""Initializes the wrangler
		"""
		pass

	def _df_pct_change(self, df, result_columns, input_columns, periods):
				"""Calculates percentage change for each period in each input column of df, appending each result column in df

				Positional Arguments:
					df: pandas dataframe
					result_columns: list of result column names (in strings)
					input_columns: list of input column names (in strings)
					periods: list of periods (in integers)
				"""
				index = 0
				for input_column in input_columns:
					for period in periods:
						df[result_columns[index]] = df[input_column].pct_change(periods=period) * 100
						index += 1

	def wrangle_data(self):
		"""Wrangles data
		"""
		print("WRANGLING AND SAVING DATA:", end="\n"*3)

		# Converts public holidays from strings to datetime objects
		sg_public_holidays_datetimes = [datetime.strptime(sg_public_holiday_date, "%Y-%m-%d") for sg_public_holiday_date in sg_public_holidays_dates]

		for stock_name, stock_ticker in sti_stocks.items():
			time.sleep(0.1)
			stock_name_no_spaces = stock_name.replace(" ", "_")
			print (f"WRANGLING AND SAVING DATA: {stock_name} {stock_ticker}", end="\n"*2)
			# Load stock's csv file with date as index
			df_original = pd.read_csv(f"sti_stock_data/original_data/daily/{stock_name_no_spaces}.csv", index_col=["date"])
			# Get stock's adjusted close and volume (previous 100 trading sessions)
			adjusted_close = df_original[["5. adjusted close", "6. volume"]]
			# Change column names
			adjusted_close.columns = ["adjusted_close", "volume"]	

			# Note:Please refer to sg_public_holidays list at the top of the file for Singapore's public holidays
			# Note:The date index currently excludes weekends and public holidays
			# Includes Singapore's public holidays in the date index, if they fall on a weekday

			# Check whether each public holiday falls within the previous 100 trading sessions' date range
			# Get start and end dates as datetime objects for the previous 100 trading sessions
			end_date = adjusted_close.index.values[0]
			end_date = datetime.strptime(end_date, "%Y-%m-%d")
			start_date = adjusted_close.index.values[-1]			
			start_date = datetime.strptime(start_date, "%Y-%m-%d")

			# Check whether each public holiday falls within date range
			for sg_public_holidays_datetime in sg_public_holidays_datetimes:
				# If public holiday falls within range, add public holiday to date index
				if start_date < sg_public_holidays_datetime < end_date:
					adjusted_close.loc[sg_public_holidays_datetime.strftime("%Y-%m-%d")] = np.nan

			# Sort stock's adjusted close series (most recent date on top)
			adjusted_close.sort_values(by="date", ascending=False, inplace=True)
			# Backward fill the NaN values with previous day's adjusted close price
			adjusted_close.fillna(method="bfill", inplace=True)

			# Calculates percentage change for each period for both price and volume
			self._df_pct_change(df=adjusted_close,
								result_columns=["price_daily_pct_change", "price_weekly_pct_change", "price_monthly_pct_change",
								"volume_daily_pct_change", "volume_weekly_pct_change", "volume_monthly_pct_change"],
								input_columns=["adjusted_close", "volume"],
								periods=[-1, -5, -20])

			# Stores adjusted_close series as csv file in sti_stock_data/wrangled_data
			adjusted_close.to_csv(f"sti_stock_data/wrangled_data/{stock_name_no_spaces}_wrangled.csv", mode="w")

			print(f"WRANGLED DATA AND SAVED: {stock_name}", end="\n"*2)
		
		print("PREPARED: ALL 30 STI STOCK DATA WRANGLED AND RESULTS SAVED", end="\n"*2)
		print("-"*20, end="\n"*2)

	def combine_data(self):
		"""Combines data
		"""
		print("COMBINING DATA:", end="\n"*2)

		price_volume_pct_change = pd.DataFrame()

		for stock_name, stock_ticker in sti_stocks.items():
			stock_name_no_spaces = stock_name.replace(" ", "_")
			df_wrangled = pd.read_csv(f"sti_stock_data/wrangled_data/{stock_name_no_spaces}_wrangled.csv", nrows=1)
			df_wrangled["stock_name_no_spaces"] = stock_name_no_spaces
			price_volume_pct_change = pd.concat([price_volume_pct_change, df_wrangled])

		price_volume_pct_change.to_csv("sti_stock_data/combined_data/combined_data.csv", mode="w")
		
		print("COMBINED: ALL WRANGLED DATA COMBINED AND RESULTS SAVED", end="\n"*2)
		print("-"*20, end="\n"*2)


if __name__ == "__main__":
	initializer = ScreenInitializer()
	initializer.initialize()
	wrangler = Wrangler()
	wrangler.wrangle_data()
	wrangler.combine_data()
	top_price_pct_change_screen = TopPricePctChangeScreen(timeframe="daily", n=5)
	top_volume_pct_change_screen = TopVolumePctChangeScreen(timeframe="daily", n=5)
	top_price_pct_change_screen.run()
	top_volume_pct_change_screen.run()
	ta_menu = TechnicalAnalysisMenu()
	ta_menu.run()
	time.sleep(10000)
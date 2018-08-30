from abc import ABC, abstractmethod
import time
from datetime import datetime
import decimal
import copy
from pprint import pprint

import pandas as pd
import numpy as np

sg_public_holidays_dates = ["2018-01-01", "2018-02-16", "2018-03-30", "2018-05-01", "2018-05-29",
                              "2018-06-15", "2018-08-09", "2018-08-22", "2018-11-06", "2018-12-25"]

sti_stocks = {"CityDev":"C09.SI", "DBS":"D05.SI", "UOL":"U14.SI", "SingTel":"Z74.SI", "UOB":"U11.SI",
                "Keppel Corp":"BN4.SI", "CapitaLand":"C31.SI", "OCBC Bank":"O39.SI", "Genting Sing":"G13.SI", "Venture":"V03.SI",
                "CapitaMall Trust":"C38U.SI", "YZJ Shipbldg SGD":"BS6.SI", "CapitaCom Trust":"C61U.SI", "Ascendas Reit":"A17U.SI", "ComfortDelGro":"C52.SI",
                "SIA":"C6L.SI", "Jardine C&C":"C07.SI", "SPH":"T39.SI", "SGX":"S68.SI", "ThaiBev":"Y92.SI",
                "ST Engineering":"S63.SI", "Sembcorp Ind":"U96.SI", "Wilmar Intl":"F34.SI", "StarHub":"CC3.SI", "SATS":"S58.SI",
                "HongkongLand USD":"H78.SI", "JSH USD":"J37.SI", "JMH USD":"J36.SI", "HPH Trust USD":"NS8U.SI", "Golden Agri-Res":"E5H.SI"}


class PrepareTechnicalAnalysis:
	"""A singleton that prepares and supplies stock data for technical analysis screens
	"""
	def __init__(self):
		self._prepare_data()

	@property
	def sti_stocks_adjusted_close(self):
		return self._sti_stocks_adjusted_close

	def _prepare_data(self):
		"""Prepares stock data for technical analysis screens
		"""
		self._sti_stocks_adjusted_close = {}
		# Converts public holidays from strings to datetime objects
		sg_public_holidays_datetimes = [datetime.strptime(sg_public_holiday_date, "%Y-%m-%d") for sg_public_holiday_date in sg_public_holidays_dates]

		for stock_name, stock_ticker in sti_stocks.items():
			time.sleep(0.1)
			stock_name_no_spaces = stock_name.replace(" ", "_")
			# Load stock's csv file with date as index
			df_original = pd.read_csv(f"sti_stock_data/original_data/daily/{stock_name_no_spaces}.csv", index_col=["date"])
			# Get stock's adjusted close (previous 100 trading sessions)
			adjusted_close = df_original[["5. adjusted close"]]
			# Change column name
			adjusted_close.columns = ["adjusted_close"]
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
			# Sort stock's adjusted close dataframe (most recent date on top)
			adjusted_close.sort_values(by="date", ascending=False, inplace=True)
			# Backward fill the NaN values with previous day's adjusted close price
			adjusted_close.fillna(method="bfill", inplace=True)
			# Sort stock's adjusted close (least recent date on top)
			adjusted_close.sort_values(by="date", ascending=True, inplace=True)
			self._sti_stocks_adjusted_close[stock_name] = adjusted_close


class TechnicalAnalysisScreener(ABC):
	"""Abstract base class for technical analysis screener
	"""
	def __init__(self):
		self._sti_stocks_adjusted_close = copy.deepcopy(prepare_ta.sti_stocks_adjusted_close)

	def _validate_input(self, prompt, input_type=None, input_range=None):
		"""Validates user input for settings of stock screen

		Positional arguments:
			prompt: user prompt for input

		Keyword arguments:
			input_type: desired type of input (eg. int) (default None)
			input_range: desired range of input (eg. range(0, 100)) (default None)
		"""
		while True:
			user_input = input(f"{prompt}\n\n")
			if input_type is not None:
				try:
					input_type(user_input)
				except ValueError:
					print(f"\n\nSupported value: {input_type.__name__}. Please try again.", end="\n"*2)
					time.sleep(0.1)
					continue
			if input_type is float:
				user_input = int(float(user_input) * 100)
				if user_input not in input_range:
					print(f"\n\nSupported range: between {input_range[0]} and {input_range[-1]}. Please try again.", end="\n"*2)
					time.sleep(0.1)
					continue
			if input_type(user_input) not in input_range:
				print(f"\n\nSupported range: between {input_range[0]} and {input_range[-1]}. Please try again.", end="\n"*2)
				time.sleep(0.1)
				continue
			return input_type(user_input)

	@abstractmethod
	def _input_settings(self):
		"""Requests user for settings, displays and validates them
		"""
		pass

	@abstractmethod
	def _screen(self):
		"""Screens stocks according to user settings
		"""
		pass

	def run(self):
		"""Runs the screener
		"""
		self._input_settings()
		self._screen()


class MACDScreener(TechnicalAnalysisScreener):
	"""Moving Average Convergence/Divergence Screener
	"""
	def __init__(self):
		"""Initializes MACD screener
		"""
		super().__init__()

	def _input_settings(self):
		"""Requests user for settings, displays and validates them
		"""
		print("\n\n\n-----MACD SCREEN-----", end="\n"*3)
		time.sleep(0.1)
		print("-----SETTINGS-----", end="\n"*3)
		time.sleep(0.1)
		print("STANDARD MACD: 12 DAY EMA - 26 DAY EMA", end="\n"*3)
		time.sleep(0.1)
		print("SIGNAL LINE: 9 DAY EMA OF MACD", end="\n"*3)
		time.sleep(0.1)

	def _screen(self):
		"""Screens stocks according to user settings
		"""
		print("SCREENING FOR SIGNAL LINE CROSSOVERS......", end="\n"*3)
		time.sleep(0.1)
		print("-"*20, end="\n"*2)
		time.sleep(0.1)

		bullish_macd_crossover = set()
		bearish_macd_crossover = set()
		no_macd_crossover = set()

		for stock_name, stock_ticker in sti_stocks.items():
			time.sleep(0.1)
			adjusted_close = self._sti_stocks_adjusted_close[stock_name]
			# Calculate stock's EWMA
			adjusted_close["12_day_ema"] = adjusted_close["adjusted_close"].ewm(span=12, min_periods=12, adjust=False).mean()
			adjusted_close["26_day_ema"] = adjusted_close["adjusted_close"].ewm(span=26, min_periods=26, adjust=False).mean()
			# Calculate stock's MACD
			adjusted_close["macd"] = adjusted_close["12_day_ema"] - adjusted_close["26_day_ema"]
			# Calculate stock's 9 day EWMA of MACD
			adjusted_close["macd_signal_line"] = adjusted_close["macd"].ewm(span=9, min_periods=9, adjust=False).mean()
			# Check for MACD bullish signal line crossover
			if (adjusted_close.iloc[-2, 4] < adjusted_close.iloc[-2, 3]) and (adjusted_close.iloc[-1, 4] > adjusted_close.iloc[-1, 3]):
				print(f"MACD BULLISH CROSSOVER DETECTED: {stock_name}", end="\n"*2)		
				bullish_macd_crossover.add(stock_name)
			# Check for MACD bearish signal line crossover
			elif (adjusted_close.iloc[-2, 4] > adjusted_close.iloc[-2, 3]) and (adjusted_close.iloc[-1, 4] < adjusted_close.iloc[-1, 3]):
				print(f"MACD BEARISH CROSSOVER DETECTED: {stock_name}", end="\n"*2)		
				bearish_macd_crossover.add(stock_name)
			else:
				print(f"NO MACD CROSSOVER DETECTED: {stock_name}", end="\n"*2)
				no_macd_crossover.add(stock_name)

		print("-----MACD SCREEN RESULTS-----", end="\n"*3)
		time.sleep(0.1)
		print("-----BULLISH CENTRELINE CROSSOVER-----", end="\n"*3)
		time.sleep(0.1)
		print(bullish_macd_crossover)
		print("-----BEARISH CENTRELINE CROSSOVER-----", end="\n"*3)
		time.sleep(0.1)
		print(bearish_macd_crossover)
		print("-----NO CENTRELINE CROSSOVER-----", end="\n"*3)
		time.sleep(0.1)
		print(no_macd_crossover)
		time.sleep(0.1)
		print("-"*20, end="\n"*3)


class RSIScreener(TechnicalAnalysisScreener):
	"""Relative Strength Index Screener
	"""
	def __init__(self):
		"""Initializes RSI screener
		"""
		super().__init__()
		self._timeframe = None
		self._overbought_level = None
		self._oversold_level = None

	def _input_settings(self):
		"""Requests user for settings, displays and validates them
		"""
		print("\n\n\n-----RSI SCREEN-----", end="\n"*3)
		time.sleep(0.1)
		print("TIMEFRAMES SUPPORTED: 2 - 99 DAYS", end="\n"*3)
		time.sleep(0.1)
		print("OVERBOUGHT VALUES SUPPORTED: 70 - 100", end="\n"*3)
		time.sleep(0.1)
		print("OVERSOLD VALUES SUPPORTED: 0 - 30", end="\n"*3)
		time.sleep(0.1)

		self._timeframe = self._validate_input("Please enter your desired screening timeframe (in days):", input_type=int, input_range=range(2, 100))
		time.sleep(0.1)
		self._overbought_level = self._validate_input("Please enter your desired overbought value (70 - 100):", input_type=int, input_range=range(70, 101))
		time.sleep(0.1)
		self._oversold_level = self._validate_input("Please enter your desired oversold value (0 - 30):", input_type=int, input_range=range(0, 31))
		time.sleep(0.1)

		print("-----SETTINGS-----", end="\n"*3)
		time.sleep(0.1)
		print(f"TIMEFRAME: {str(self._timeframe)}", end="\n"*3)
		time.sleep(0.1)
		print(f"OVERBOUGHT AT OR ABOVE: {str(self._overbought_level)}", end="\n"*3)
		time.sleep(0.1)
		print(f"OVERSOLD AT OR BELOW: {str(self._oversold_level)}", end="\n"*3)
		time.sleep(0.1)

	def _screen(self):
		"""Screens stocks according to user settings
		"""
		print("SCREENING FOR OVERBOUGHT AND OVERSOLD STOCKS......", end="\n"*3)
		time.sleep(0.1)
		print("-"*20, end="\n"*2)
		time.sleep(0.1)

		rsi_overbought = {}
		rsi_oversold = {}
		rsi_neutral = {}

		for stock_name, stock_ticker in sti_stocks.items():
			time.sleep(0.1)
			adjusted_close = self._sti_stocks_adjusted_close[stock_name]
			# Calculate stock's daily changes in adjusted closing price
			adjusted_close["daily_price_change"] = adjusted_close["adjusted_close"].diff(periods=1)
			# Calculate stock's daily changes for up and down days
			adjusted_close["daily_price_gain"] = adjusted_close["daily_price_change"].apply(lambda x: 0 if x < 0 else x)
			adjusted_close["daily_price_loss"] = adjusted_close["daily_price_change"].apply(lambda x: 0 if x > 0 else -x)
			# Calculate stock's rolling mean for up and down days
			rolling_mean_price_gain = adjusted_close["daily_price_gain"].rolling(self._timeframe).mean().to_frame("rolling_mean_price_gain")
			rolling_mean_price_loss = adjusted_close["daily_price_loss"].rolling(self._timeframe).mean().to_frame("rolling_mean_price_loss")
			# Calculate stock's adjusted rolling mean for up and down days (see: https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:relative_strength_index_rsi)
			rolling_mean_price_gain["shifted_rolling_mean_price_gain"] = rolling_mean_price_gain["rolling_mean_price_gain"].shift(1)
			rolling_mean_price_loss["shifted_rolling_mean_price_loss"] = rolling_mean_price_loss["rolling_mean_price_loss"].shift(1)
			rolling_mean_price_gain["adjusted_rolling_mean_price_gain"] = ((rolling_mean_price_gain["shifted_rolling_mean_price_gain"] * (self._timeframe - 1)) + adjusted_close["daily_price_gain"]) / self._timeframe
			rolling_mean_price_loss["adjusted_rolling_mean_price_loss"] = ((rolling_mean_price_loss["shifted_rolling_mean_price_loss"] * (self._timeframe - 1)) + adjusted_close["daily_price_loss"]) / self._timeframe
			# Add stock's first average gain/loss
			rolling_mean_price_gain.iloc[self._timeframe, 2] = rolling_mean_price_gain.iloc[self._timeframe, 0]
			rolling_mean_price_loss.iloc[self._timeframe, 2] = rolling_mean_price_loss.iloc[self._timeframe, 0]
			# Calculate stock's relative strength
			relative_strength = (rolling_mean_price_gain["adjusted_rolling_mean_price_gain"] / rolling_mean_price_loss["adjusted_rolling_mean_price_loss"]).to_frame("relative_strength")
			# Calculate stock's relative strength index
			relative_strength["relative_strength_index"] = 100 - (100 / (1 + relative_strength["relative_strength"]))
			rsi = relative_strength.iloc[-1, 1]
			# Check whether stock is overbought according to RSI
			if rsi >= self._overbought_level:
				print(f"OVERBOUGHT STOCK: {stock_name}", end="\n"*2)
				rsi_overbought[stock_name] = rsi
			# Check whether stock is oversold according to RSI
			elif rsi <= self._oversold_level:
				print(f"OVERSOLD STOCK: {stock_name}", end="\n"*2)
				rsi_oversold[stock_name] = rsi
			else:
				print(f"NEUTRAL STOCK: {stock_name}", end="\n"*2)
				rsi_neutral[stock_name] = rsi

		#Sort results
		rsi_overbought_sorted = sorted(rsi_overbought.items(), key=lambda x: x[1], reverse=True)
		rsi_neutral_sorted = sorted(rsi_neutral.items(), key=lambda x: x[1], reverse=True)
		rsi_oversold_sorted = sorted(rsi_oversold.items(), key=lambda x: x[1])	
		#Convert results to dataframes
		df_rsi_overbought = pd.DataFrame(rsi_overbought_sorted, columns=["Company", "Relative Strength Index"])
		df_rsi_neutral = pd.DataFrame(rsi_neutral_sorted, columns=["Company", "Relative Strength Index"])
		df_rsi_oversold = pd.DataFrame(rsi_oversold_sorted, columns=["Company", "Relative Strength Index"])
		
		print("-----RSI SCREEN RESULTS-----", end="\n"*3)
		time.sleep(0.1)
		print("-----RSI OVERBOUGHT-----", end="\n"*3)
		time.sleep(0.1)
		print(df_rsi_overbought)
		print("-----RSI OVERSOLD-----", end="\n"*3)
		time.sleep(0.1)
		print(df_rsi_oversold)
		print("-----RSI NEUTRAL-----", end="\n"*3)
		time.sleep(0.1)
		print(df_rsi_neutral)
		time.sleep(0.1)
		print("-"*20, end="\n"*3)


class StochRSIScreener(TechnicalAnalysisScreener):
	"""Stochastic Relative Strength Index Screener
	"""
	def __init__(self):
		"""Initializes StochRSIScreener
		"""
		super().__init__()
		self._timeframe = None
		self._overbought_level = None
		self._oversold_level = None

	def _input_settings(self):
		"""Requests user for settings, displays and validates them
		"""
		print("\n\n\n-----STOCHASTIC RSI SCREEN-----", end="\n"*3)
		time.sleep(0.1)
		print("TIMEFRAMES SUPPORTED: 2 - 97 DAYS", end="\n"*3)
		time.sleep(0.1)
		print("OVERBOUGHT VALUES SUPPORTED: 0.7 - 1", end="\n"*3)
		time.sleep(0.1)
		print("OVERSOLD VALUES SUPPORTED: 0 - 0.3", end="\n"*3)
		time.sleep(0.1)

		self._timeframe = self._validate_input("Please enter your desired screening timeframe (in days):", input_type=int, input_range=range(2, 98))
		time.sleep(0.1)
		self._overbought_level = self._validate_input("Please enter your desired overbought value (0.7 - 1):", input_type=float, input_range=range(70, 101))
		time.sleep(0.1)
		self._oversold_level = self._validate_input("Please enter your desired oversold value (0 - 0.3):", input_type=float, input_range=range(0, 31))
		time.sleep(0.1)

		print("-----SETTINGS-----", end="\n"*3)
		time.sleep(0.1)
		print(f"TIMEFRAME: {str(self._timeframe)}", end="\n"*3)
		time.sleep(0.1)
		print(f"OVERBOUGHT AT OR ABOVE: {str(self._overbought_level)}", end="\n"*3)
		time.sleep(0.1)
		print(f"OVERSOLD AT OR BELOW: {str(self._oversold_level)}", end="\n"*3)
		time.sleep(0.1)

	def _screen(self):
		"""Screens stocks according to user settings
		"""
		print("SCREENING FOR OVERBOUGHT AND OVERSOLD STOCKS......", end="\n"*3)
		time.sleep(0.1)
		print("-"*20, end="\n"*2)
		time.sleep(0.1)

		stochrsi_overbought = {}
		stochrsi_oversold = {}
		stochrsi_neutral = {}

		for stock_name, stock_ticker in sti_stocks.items():
			time.sleep(0.1)
			adjusted_close = self._sti_stocks_adjusted_close[stock_name]
			# Calculate stock's daily changes in adjusted closing price
			adjusted_close["daily_price_change"] = adjusted_close["adjusted_close"].diff(periods=1)
			# Calculate stock's daily changes for up and down days
			adjusted_close["daily_price_gain"] = adjusted_close["daily_price_change"].apply(lambda x: 0 if x < 0 else x)
			adjusted_close["daily_price_loss"] = adjusted_close["daily_price_change"].apply(lambda x: 0 if x > 0 else -x)
			# Calculate stock's rolling mean for up and down days
			rolling_mean_price_gain = adjusted_close["daily_price_gain"].rolling(self._timeframe).mean().to_frame("rolling_mean_price_gain")
			rolling_mean_price_loss = adjusted_close["daily_price_loss"].rolling(self._timeframe).mean().to_frame("rolling_mean_price_loss")
			# Calculate stock's adjusted rolling mean for up and down days (see: https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:relative_strength_index_rsi)
			rolling_mean_price_gain["shifted_rolling_mean_price_gain"] = rolling_mean_price_gain["rolling_mean_price_gain"].shift(1)
			rolling_mean_price_loss["shifted_rolling_mean_price_loss"] = rolling_mean_price_loss["rolling_mean_price_loss"].shift(1)
			rolling_mean_price_gain["adjusted_rolling_mean_price_gain"] = ((rolling_mean_price_gain["shifted_rolling_mean_price_gain"] * (self._timeframe - 1)) + adjusted_close["daily_price_gain"]) / self._timeframe
			rolling_mean_price_loss["adjusted_rolling_mean_price_loss"] = ((rolling_mean_price_loss["shifted_rolling_mean_price_loss"] * (self._timeframe - 1)) + adjusted_close["daily_price_loss"]) / self._timeframe
			# Add stock's first average gain/loss
			rolling_mean_price_gain.iloc[self._timeframe, 2] = rolling_mean_price_gain.iloc[self._timeframe, 0]
			rolling_mean_price_loss.iloc[self._timeframe, 2] = rolling_mean_price_loss.iloc[self._timeframe, 0]
			# Calculate stock's relative strength
			relative_strength = (rolling_mean_price_gain["adjusted_rolling_mean_price_gain"] / rolling_mean_price_loss["adjusted_rolling_mean_price_loss"]).to_frame("relative_strength")
			# Calculate stock's relative strength index
			relative_strength["relative_strength_index"] = 100 - (100 / (1 + relative_strength["relative_strength"]))
			# Calculate stock's highest rsi and lowest rsi in a given timeframe
			relative_strength["rolling_max_relative_strength_index"] = relative_strength["relative_strength_index"].rolling(self._timeframe).max()
			relative_strength["rolling_min_relative_strength_index"] = relative_strength["relative_strength_index"].rolling(self._timeframe).min()
			# Calculate stock's stochastic relative strength index
			stochastic_relative_strength_index = ((relative_strength["relative_strength_index"] - relative_strength["rolling_min_relative_strength_index"]) / (relative_strength["rolling_max_relative_strength_index"] - relative_strength["rolling_min_relative_strength_index"])).to_frame("stochastic_relative_strength_index")
			stoch_rsi = stochastic_relative_strength_index.iloc[-1, 0]
			# Check whether stock is overbought according to StochRSI
			if stoch_rsi >= self._overbought_level:
				print(f"OVERBOUGHT STOCK: {stock_name}", end="\n"*2)
				stochrsi_overbought[stock_name] = stoch_rsi
			# Check whether stock is oversold according to StochRSI
			elif stoch_rsi <= self._oversold_level:
				print(f"OVERSOLD STOCK: {stock_name}", end="\n"*2)
				stochrsi_oversold[stock_name] = stoch_rsi
			else:
				print(f"NEUTRAL STOCK: {stock_name}", end="\n"*2)
				stochrsi_neutral[stock_name] = stoch_rsi
		# Sort results
		stochrsi_overbought_sorted = sorted(stochrsi_overbought.items(), key =lambda x: x[1], reverse=True)
		stochrsi_oversold_sorted = sorted(stochrsi_oversold.items(), key=lambda x: x[1])
		stochrsi_neutral_sorted = sorted(stochrsi_neutral.items(), key=lambda x: x[1], reverse=True)
		# Convert results to dataframes
		df_stochrsi_overbought = pd.DataFrame(stochrsi_overbought_sorted, columns=["Company", "Stochastic Relative Strength Index"])
		df_stochrsi_oversold = pd.DataFrame(stochrsi_oversold_sorted, columns=["Company", "Stochastic Relative Strength Index"])
		df_stochrsi_neutral = pd.DataFrame(stochrsi_neutral_sorted, columns=["Company", "Stochastic Relative Strength Index"])
		
		print("-----STOCHRSI SCREEN RESULTS-----", end="\n"*3)
		time.sleep(0.1)
		print("-----STOCHRSI OVERBOUGHT-----", end="\n"*3)
		time.sleep(0.1)
		print(df_stochrsi_overbought)
		print("-----STOCHRSI OVERSOLD-----", end="\n"*3)
		time.sleep(0.1)
		print(df_stochrsi_oversold)
		print("-----STOCHRSI NEUTRAL-----", end="\n"*3)
		time.sleep(0.1)
		print(df_stochrsi_neutral)
		time.sleep(0.1)
		print("-"*20, end="\n"*3)


prepare_ta = PrepareTechnicalAnalysis()
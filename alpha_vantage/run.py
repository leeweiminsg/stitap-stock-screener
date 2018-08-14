import time
from datetime import datetime
import json
import decimal
from pprint import pprint

import pandas as pd
import numpy as np

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

sg_public_holidays_dates = ["2018-01-01", "2018-02-16", "2018-02-17", "2018-03-30", "2018-05-01", "2018-05-29",
					  "2018-06-15", "2018-08-09", "2018-08-22", "2018-11-06", "2018-12-25"]

sti_stocks = {"CityDev":"C09.SI", "DBS":"D05.SI", "UOL":"U14.SI", "SingTel":"Z74.SI", "UOB":"U11.SI",
				"Keppel Corp":"BN4.SI", "CapitaLand":"C31.SI", "OCBC Bank":"O39.SI", "Genting Sing":"G13.SI", "Venture":"V03.SI",
				"CapitaMall Trust":"C38U.SI", "YZJ Shipbldg SGD":"BS6.SI", "CapitaCom Trust":"C61U.SI", "Ascendas Reit":"A17U.SI", "ComfortDelGro":"C52.SI",
				"SIA":"C6L.SI", "Jardine C&C":"C07.SI", "SPH":"T39.SI", "SGX":"S68.SI", "ThaiBev":"Y92.SI",
				"ST Engineering":"S63.SI", "Sembcorp Ind":"U96.SI", "Wilmar Intl":"F34.SI", "StarHub":"CC3.SI", "SATS":"S58.SI",
				"HongkongLand USD":"H78.SI", "JSH USD":"J37.SI", "JMH USD":"J36.SI", "HPH Trust USD":"NS8U.SI", "Golden Agri-Res":"E5H.SI"}


def initialize(backtest = None):
	"""Initializes the program by fetching and storing data
	Keyword arguments:
		backtest: Initializes program for backtesting if value is not None
			None: Initializes screener
			"daily": Initializes backtest (daily timeframe)
			"weekly": Initializes backtest (weekly timeframe)
			"monthly": Initializes backtest (monthly timeframe)
	"""

	ts = TimeSeries(key = "", output_format = "pandas") # <--- SET API KEY HERE

	print("-----Straits Times Index Technical Analysis Project: STITAP-----", end = "\n"*3)
	time.sleep(0.1)

	print("-----V1.1-----", end = "\n"*3)
	time.sleep(0.1)

	print(f"INITIALIZING: LOADING AND SAVING ALL 30 STI STOCK DATA (backtest = {backtest}):", end = "\n"*3)
	time.sleep(0.1)

	for company_name, company_ticker in sti_stocks.items():
		time.sleep(0.1)
		print (f"LOADING: {company_name} {company_ticker}", end = "\n"*2)
		company_name_no_spaces = company_name.replace(" ", "_")
		time.sleep(60) # <--- Adjust the duration (No. of seconds) of waiting time between each API call here

		#Initializes program according to value of backtest argument
		if backtest is None:
			#Makes API call
			data, meta_data  = ts.get_daily_adjusted(symbol = company_ticker)

		elif backtest == "daily":
			data, meta_data  = ts.get_daily_adjusted(symbol = company_ticker, outputsize = "full")

		elif backtest == "weekly":
			data, meta_data  = ts.get_weekly_adjusted(symbol = company_ticker)

		elif backtest == "monthly":
			data, meta_data  = ts.get_monthly_adjusted(symbol = company_ticker)

		#Sorts the resulting data pandas object in order of recency (latest date on top)
		data.sort_index(ascending = False, inplace = True)

		if backtest is None:
			#Stores the csv file to sti_stock_data/original_data
			data.to_csv(f"sti_stock_data/original_data/{company_name_no_spaces}.csv", mode = "w")

		else:
			data.to_csv(f"sti_stock_data/backtest_data/{backtest}/{company_name_no_spaces}.csv", mode = "w")
		
		print (f"LOADED AND SAVED: {company_name}", end = "\n"*2)

	print(f"INITIALIZED: ALL 30 STI STOCK DATA LOADED AND SAVED (backtest = {backtest})", end = "\n"*2)
	print("-"*20, end = "\n"*2)


def wrangle_data():

	print("WRANGLING AND SAVING DATA:\n\n")

	#Creates a new list for public holidays converted to datetime objects
	sg_public_holidays_datetimes = []

	#Converts public holidays from strings to datetime objects before adding to the list
	for sg_public_holiday_date in sg_public_holidays_dates:
		sg_public_holidays_datetimes.append(datetime.strptime(sg_public_holiday_date, "%Y-%m-%d"))

	for company_name, company_ticker in sti_stocks.items():
		time.sleep(0.1)
		company_name_no_spaces = company_name.replace(" ", "_")
		print ("WRANGLING AND SAVING DATA: " + company_name + " " + company_ticker + "\n")
		#Load stock's csv file with date as index
		df_original = pd.read_csv("sti_stock_data/original_data/" + company_name_no_spaces + ".csv", index_col = ["date"])
		#Get stock's adjusted close and volume (previous 100 trading sessions)
		adjusted_close = df_original[["5. adjusted close", "6. volume"]]
		#Note: The date index currently excludes weekends and public holidays.
		#Note: Please refer to sg_public_holidays list at the top of the file for Singapore's public holidays
		#Include Singapore's public holidays in the date index.

		#Check whether each public holiday falls within the previous 100 trading sessions' date range
		#Get start and end dates (in strings) for the previous 100 trading sessions
		end_date = adjusted_close.index.values[0]
		start_date = adjusted_close.index.values[-1]

		#Get start and end dates as datetime objects
		end_date = datetime.strptime(end_date, "%Y-%m-%d")
		start_date = datetime.strptime(start_date, "%Y-%m-%d")

		#Check whether each public holiday falls within date range
		for sg_public_holidays_datetime in sg_public_holidays_datetimes:
			#If public holiday falls within range, add public holiday to date index
			if start_date < sg_public_holidays_datetime < end_date:
				adjusted_close.loc[sg_public_holidays_datetime.strftime("%Y-%m-%d")] = np.nan

		#Convert pandas series to dataframe
		#adjusted_close = adjusted_close.to_frame()

		#Sort stock's adjusted close series (most recent date on top)
		adjusted_close.sort_values(by = "date", ascending = False, inplace = True)

		#Backward fill the NaN values with previous day's adjusted close price
		adjusted_close.fillna(method = "bfill", inplace = True)

		#Calculate daily percentage change in adjusted close prices
		adjusted_close["daily_price_pct_change"] = adjusted_close["5. adjusted close"].pct_change(periods = -1)
		adjusted_close["daily_price_pct_change"] = adjusted_close["daily_price_pct_change"] * 100

		#Calculate weekly percentage change in adjusted close prices
		adjusted_close["weekly_price_pct_change"] = adjusted_close["5. adjusted close"].pct_change(periods = -5)
		adjusted_close["weekly_price_pct_change"] = adjusted_close["weekly_price_pct_change"] * 100

		#Calculate monthly percentage change in adjusted close prices
		adjusted_close["monthly_price_pct_change"] = adjusted_close["5. adjusted close"].pct_change(periods = -20)
		adjusted_close["monthly_price_pct_change"] = adjusted_close["monthly_price_pct_change"] * 100

		#Calculate daily percentage change in volume
		adjusted_close["daily_volume_pct_change"] = adjusted_close["6. volume"].pct_change(periods = -1)
		adjusted_close["daily_volume_pct_change"] = adjusted_close["daily_volume_pct_change"] * 100

		#Calculate weekly percentage change in volume
		adjusted_close["weekly_volume_pct_change"] = adjusted_close["6. volume"].pct_change(periods = -5)
		adjusted_close["weekly_volume_pct_change"] = adjusted_close["weekly_volume_pct_change"] * 100

		#Calculate monthly percentage change in volume
		adjusted_close["monthly_volume_pct_change"] = adjusted_close["6. volume"].pct_change(periods = -20)
		adjusted_close["monthly_volume_pct_change"] = adjusted_close["monthly_volume_pct_change"] * 100

		#Stores adjusted_close series as csv file in sti_stock_data/wrangled_data
		adjusted_close.to_csv("sti_stock_data/wrangled_data/" + company_name_no_spaces + "_wrangled.csv", mode = "w")

		print ("\nWRANGLED DATA AND SAVED: " + company_name + "\n\n")		
	
	print("PREPARED: ALL 30 STI STOCK DATA WRANGLED AND RESULTS SAVED\n\n")
	print("---------------------------------------------------------------\n\n")


def combine_data():

	print("COMBINING DATA:\n\n")

	price_volume_pct_change = pd.DataFrame()

	for company_name, company_ticker in sti_stocks.items():
		company_name_no_spaces = company_name.replace(" ", "_")

		#Read csv file and organise the stock data
		df_wrangled = pd.read_csv("sti_stock_data/wrangled_data/" + company_name_no_spaces + "_wrangled.csv", nrows = 1)

		#Add company name column
		df_wrangled["company_name_no_spaces"] = company_name_no_spaces

		price_volume_pct_change = pd.concat([price_volume_pct_change, df_wrangled])

	price_volume_pct_change.to_csv("sti_stock_data/combined_data/combined_data.csv", mode = "w")
	
	print("COMBINED: ALL WRANGLED DATA COMBINED AND RESULTS SAVED\n\n")
	print("---------------------------------------------------------------\n\n")


def price_volume_top_pct_change_screener(screen = "price", timeframe = "daily"):
	"""
	Keyword arguments:
		screen: type of stock screen, supported values are:
			"price": filters top and bottom 5 stocks of the Straits Times Index in terms of percentage price changes
			"volume": filters top and bottom 5 stocks of the Straits Times Index in terms of percentage volume changes
		timeframe: sets the timeframe for the screen, supported values are:
			"daily": timeframe set to 1 day
			"weekly": timeframe set to 1 week
			"monthly": timeframe set to 1 month
	"""

	#Filter stocks for top 5 price or volume increases and declines of the Straits Times Index depending on the timeframe set
	df_combined = pd.read_csv("sti_stock_data/combined_data/combined_data.csv")

	print("TOP 5 STI STOCKS WITH HIGHEST PERCENTAGE CHANGE IN " + screen.upper() + ": " + timeframe.upper() + " SCREEN\n\n")
	print("---------------------\n\n")
	top_five = df_combined.nlargest(n = 5, columns = timeframe + "_" + screen + "_pct_change")
	top_five = top_five[["company_name_no_spaces", timeframe +"_" + screen + "_pct_change"]]
	pprint(top_five)
	print("\n\n---------------------\n\n")

	print("TOP 5 STI STOCKS WITH LOWEST PERCENTAGE CHANGE IN " + screen.upper() + ": " + timeframe.upper() + " SCREEN\n\n")
	print("---------------------\n\n")
	bottom_five = df_combined.nsmallest(n = 5, columns = timeframe + "_" + screen + "_pct_change")
	bottom_five = bottom_five[["company_name_no_spaces", timeframe +"_" + screen + "_pct_change"]]
	pprint(bottom_five)
	print("\n\n---------------------\n\n")


def technical_analysis_menu():
	"""
	Displays menu for technical screen.
	Requires user input.
	"""

	print("----------STITAP TECHNICAL ANALYSIS SCREENER----------\n\n")
	time.sleep(0.1)

	print("-----CURRENTLY SUPPORTS 3 TECHNICAL SCREENS-----\n\n")
	time.sleep(0.1)

	print("-----MORE IN THE FUTURE-----\n\n")
	time.sleep(0.1)

	print("Please enter your desired technical analysis screener below (the symbol to the right) in UPPERCASE:\n\n")
	time.sleep(0.1)

	technical_analysis_screens = {"Moving Average Convergence / Divergence":"MACD",
								  "Relative Strength Index":"RSI", "Stochastic Relative Strength Index":"STOCHRSI"}
	
	while True:

		screen = input("Moving Average Convergence / Divergence - MACD\n\n" + \
					   "Relative Strength Index - RSI\n\n" + \
					   "Stochastic Relative Strength Index - STOCHRSI\n\n")

		if screen in technical_analysis_screens.values():
			time.sleep(0.1)
			print("\n\n" + screen + " SELECTED.\n\n")
			time.sleep(0.1)
			break

		else:
			print("\n\nInvalid input. Please try again.\n\n")

	technical_analysis_screener(screen)


def validate_input(prompt, input_type = None, input_range = None):
	"""
	Generic function for validating user input for parameters of the stock screen.
	Keyword arguments:
		prompt: user prompt for input eg.("Please enter a number:")
		input_type: type of desired input. eg.(int)
		input_range: range of input. eg.(range(0, 100))
	"""

	while True:
		user_input= input("\n\n" + prompt + "\n\n")

		if input_type is not None:
			try:
				input_type(user_input)
			except ValueError:
				print("\n\nSupported value: {0}. Please try again.\n\n".format(input_type.__name__))
				time.sleep(0.1)
				continue
		if input_range is not None and input_type(user_input) not in input_range:
			print("\n\nPlease input a value between {0} and {1}.\n\n".format(input_range[0], input_range[-1]))
			time.sleep(0.1)
			continue
		else:
			return input_type(user_input)


def technical_analysis_screener(screen):
	"""
	Identifies and flags out stocks with extreme and/or unusual values based on the type of technical screen.
	Keyword arguments:
		screen: type of technical indicator to be used for screening
			"BBANDS": Bollinger Bands 
			"MACD": Moving Average Convergence / Divergence
			"RSI": Relative Strength Index
			"STOCHRSI": Stochastic Relative Strength Index
	"""

	technical_analysis_functions = {"MACD":moving_average_convergence_divergence_screener,
									"RSI":relative_strength_index_screener,
									"STOCHRSI":relative_strength_index_screener}

	print("----------SETTINGS FOR " + screen + ":----------\n\n")
	time.sleep(0.1)

	print("ABOUT " + screen + " SCREEN:\n\n")
	time.sleep(0.1)

	if screen == "STOCHRSI":
		print("TIMEFRAMES SUPPORTED: 2 - 97 DAYS\n\n")
		time.sleep(0.1)

		print("OVERBOUGHT AND OVERSOLD VALUES FIXED AT 0.8 AND 0.2 RESPECTIVELY\n\n")
		time.sleep(0.1)

		timeframe_i = validate_input("Please enter your desired timeframe (in days):", input_type = int, input_range = range(2, 100))
		time.sleep(0.1)		
		"""
		Below code is not supported. Range() does not support floating point numbers. Will fix in future.

		upperbound_i = validate_input("Please enter your desired RSI overbought value:", input_type = int, input_range = range(0.7, 1))
		time.sleep(0.1)
		
		lowerbound_i = validate_input("Please enter your desired RSI oversold value:", input_type = int, input_range = range(0, 31))
		time.sleep(0.1)"""		
		stochastic_relative_strength_index_screener(timeframe = timeframe_i, upperbound = 0.8, lowerbound = 0.2)

	elif screen == "MACD":
		moving_average_convergence_divergence_screener()

	elif screen == "RSI":
		print("TIMEFRAMES SUPPORTED: 2 - 99 DAYS\n\n")
		time.sleep(0.1)

		print("OVERBOUGHT VALUES SUPPORTED: 70 - 100\n\n")
		time.sleep(0.1)

		print("OVERSOLD VALUES SUPPORTED: 0 - 30\n\n")
		time.sleep(0.1)	

		timeframe_i = validate_input("Please enter your desired timeframe (in days):", input_type = int, input_range = range(2, 100))
		time.sleep(0.1)

		upperbound_i = validate_input("Please enter your desired overbought value (70 - 100):", input_type = int, input_range = range(70, 101))
		time.sleep(0.1)

		lowerbound_i = validate_input("Please enter your desired oversold value (0 - 30):", input_type = int, input_range = range(0, 31))
		time.sleep(0.1)

		relative_strength_index_screener(timeframe = timeframe_i, upperbound = upperbound_i, lowerbound = lowerbound_i)

	else:
		return


def moving_average_convergence_divergence_screener():
	"""
	Moving Average Convergence / Divergence screener
	"""

	print("\n\n----------MACD SCREEN----------\n\n")
	time.sleep(0.1)
	print("----------SETTINGS----------\n\n")
	time.sleep(0.1)

	print("STANDARD MACD -> (12 DAY EMA - 26 DAY EMA)\n\n")
	time.sleep(0.1)
	print("SIGNAL LINE -> 9 DAY EMA OF MACD\n\n")
	time.sleep(0.1)
	print("SCREENING FOR SIGNAL LINE CROSSOVERS......\n\n")
	time.sleep(0.1)

	bullish_centreline_crossover = {}

	bearish_centreline_crossover = {}

	for company_name, company_ticker in sti_stocks.items():
		company_name_no_spaces = company_name.replace(" ", "_")

		#Read csv file
		df_original = pd.read_csv("sti_stock_data/original_data/" + company_name_no_spaces + ".csv", index_col = 0)

		#Prepare pandas series for calculations
		df_technical_timeframe = df_original.head(100)
		df_technical_timeframe_adjusted_close = df_technical_timeframe["5. adjusted close"]
		df_technical_timeframe_adjusted_close_reversed = df_technical_timeframe_adjusted_close.iloc[::-1]

		df_12_day_ema = df_technical_timeframe_adjusted_close_reversed.ewm(span = 12, min_periods = 12, adjust = False).mean()
		df_26_day_ema = df_technical_timeframe_adjusted_close_reversed.ewm(span = 26, min_periods = 26, adjust = False).mean()

		df_macd = df_12_day_ema - df_26_day_ema

		macd = df_macd.tail(2)

		macd_signal_line = df_macd.ewm(span = 9, min_periods = 9, adjust = False).mean()

		macd_signal = macd_signal_line.tail(2)



		if ((macd.loc[0, ] - macd_signal.loc[0, ]) <= 0) and ((macd.loc[0, ] - macd_signal.loc[0, ]) > 0):
			bullish_centreline_crossover[company_name] = "Bullish Crossover Detected"

		elif ((macd.loc[0, ] - macd_signal.loc[0, ]) >= 0) and ((macd.loc[0, ] - macd_signal.loc[0, ]) < 0):
			bearish_centreline_crossover[company_name] = "Bearish Crossover Detected"

		else:
			continue

	print("----------MACD SCREEN RESULTS----------\n\n")
	time.sleep(0.1)
	print("-----BULLISH CENTRELINE CROSSOVER-----\n\n")
	time.sleep(0.1)

	bullish_centreline_crossover_sorted = pd.DataFrame(bullish_centreline_crossover, columns = ["Company", "Results"])
	pprint(bullish_centreline_crossover_sorted)

	print("\n\n-----BEARISH CENTRELINE CROSSOVER-----\n\n")
	time.sleep(0.1)

	dbearish_centreline_crossover_sorted = pd.DataFrame(bearish_centreline_crossover, columns = ["Company", "Results"])
	pprint(dbearish_centreline_crossover_sorted)

	print("\n\n--------------------\n\n")

	technical_analysis_menu()


def relative_strength_index_screener(timeframe = 14, upperbound = 70, lowerbound = 30):
	"""
	Relative Strength Index screener
	Keyword Arguments (set by user during runtime):
		timeframe: Sets the timeframe (number of trading sessions) (daily) for RSI screen. Supported values are between 2 and 99 (inclusive) atm.
		upperbound: Sets the rsi value such that any stock with rsi >= upperbound is considered overbought. Supported values are between 70 and 100 (inclusive).
		lowerbound: Sets the rsi value such that any stock with rsi <= lowerbound is considered oversold. Supported values are between 0 and 30 (inclusive).
	"""

	print("\n\n----------RSI SCREEN----------\n\n")
	time.sleep(0.1)
	print("----------SETTINGS----------\n\n")
	time.sleep(0.1)

	print("TIMEFRAME: " + str(timeframe) + "\n\n")
	time.sleep(0.1)
	print("OVERBOUGHT AT OR ABOVE: " + str(upperbound) + "\n\n")
	time.sleep(0.1)
	print("OVERSOLD AT OR BELOW: " + str(lowerbound) + "\n\n")
	time.sleep(0.1)
	print("SCREENING......\n\n")
	time.sleep(0.1)

	rsi_overbought = {}
	rsi_oversold = {}
	rsi_neutral = {}
	
	for company_name, company_ticker in sti_stocks.items():
		company_name_no_spaces = company_name.replace(" ", "_")

		#Load stock's csv file with date as index
		df_original = pd.read_csv("sti_stock_data/original_data/" + company_name_no_spaces + ".csv", index_col = ["date"])

		#Get stock's adjusted close series (previous 100 trading sessions)
		df_rsi = df_original[["5. adjusted close"]]

		#Calculate stock's daily adjusted close changes
		df_rsi["daily_price_change"] = df_rsi["5. adjusted close"].diff(periods = -1)

		#Remove last row due which has NaN value
		df_rsi = df_rsi[:-1]	

		#Reverse dataframe
		df_rsi.sort_values(by = ["date"], inplace = True)

		#Get two copies of daily_price_change dataframe for filtering values
		df_rsi_up = df_rsi["daily_price_change"]
		df_rsi_down = df_rsi["daily_price_change"]

		#Filter the gains and losses in each copy
		df_rsi_up = df_rsi_up.apply(lambda x: 0 if x < 0 else x)
		df_rsi_down = df_rsi_down.apply(lambda x: 0 if x > 0 else x)

		#Merge dataframes
		df_rsi["daily_price_increase"] = df_rsi_up
		df_rsi["daily_price_decrease"] = df_rsi_down

		#Calculate average gain and loss over the specified timeframe
		df_rsi_up_rolling_mean = df_rsi_up.rolling(window = timeframe).mean()
		df_rsi_down_rolling_mean = df_rsi_down.abs().rolling(window = timeframe).mean()

		#Merge into main fataframe
		df_rsi["daily_price_increase_rolling_mean"] = df_rsi_up_rolling_mean
		df_rsi["daily_price_decrease_rolling_mean"] = df_rsi_down_rolling_mean

		#Remove first (timeframe - 1) rows which have NaN values
		df_rsi = df_rsi[timeframe - 1:]

		#Get subset of dataframe depending on the timeframe
		df_rsi = df_rsi[-timeframe:]

		#Shift daily_price_increase_rolling_mean and daily_price_decrease_rolling_mean columns down by 1 row for rest of relative strength calculations
		df_rsi["daily_price_increase_rolling_mean_calc"] = df_rsi["daily_price_increase_rolling_mean"].shift(1)
		df_rsi["daily_price_decrease_rolling_mean_calc"] = df_rsi["daily_price_decrease_rolling_mean"].shift(1)

		#Calculate average price increase / decrease for rest of the rows
		df_rsi["daily_price_average_increase"] = ((df_rsi["daily_price_increase_rolling_mean_calc"] * (timeframe - 1)) + df_rsi["daily_price_increase"]) / timeframe
		df_rsi["daily_price_average_decrease"] = ((df_rsi["daily_price_decrease_rolling_mean_calc"] * (timeframe - 1)) + df_rsi["daily_price_decrease"]) / timeframe

		#Calculate average price increase / decrease for first row
		df_rsi.iloc[0, 8] = df_rsi.iloc[0, 4] / timeframe
		df_rsi.iloc[0, 9] = df_rsi.iloc[0, 5] / timeframe

		#Calculate relative strength
		df_rsi["relative_strength"] = df_rsi["daily_price_average_increase"] / df_rsi["daily_price_average_decrease"]

		#Calculate relative strength index
		df_rsi["relative_strength_index"] = 100 - (100 / (1 + df_rsi["relative_strength"]))

		#Convert to two decimal places
		df_rsi["relative_strength_index"] = df_rsi["relative_strength_index"].round(decimals = 2)

		#Get the current day's rsi value
		rsi = df_rsi.iloc[-1, 11]

		#Classify rsi values accordingly
		if rsi >= upperbound:
			rsi_overbought[company_name] = rsi
		elif rsi <= lowerbound:
			rsi_oversold[company_name] = rsi
		else:
			rsi_neutral[company_name] = rsi

	#Sort results
	rsi_overbought_sorted = sorted(rsi_overbought.items(), key = lambda x: x[1], reverse = True)
	rsi_neutral_sorted = sorted(rsi_neutral.items(), key = lambda x: x[1], reverse = True)
	rsi_oversold_sorted = sorted(rsi_oversold.items(), key = lambda x: x[1])	

	#Convert results to dataframes
	df_rsi_overbought = pd.DataFrame(rsi_overbought_sorted, columns = ["Company", "Relative Strength Index"])
	df_rsi_neutral = pd.DataFrame(rsi_neutral_sorted, columns = ["Company", "Relative Strength Index"])
	df_rsi_oversold = pd.DataFrame(rsi_oversold_sorted, columns = ["Company", "Relative Strength Index"])

	print("----------RSI SCREEN RESULTS----------\n\n")
	time.sleep(0.1)
	print("-----OVERBOUGHT-----\n\n")
	time.sleep(0.1)

	pprint(df_rsi_overbought)

	print("\n\n-----NEUTRAL-----\n\n")
	time.sleep(0.1)

	pprint(df_rsi_neutral)

	print("\n\n-----OVERSOLD-----\n\n")
	time.sleep(0.1)

	pprint(df_rsi_oversold)

	print("\n\n--------------------\n\n")

	technical_analysis_menu()


def stochastic_relative_strength_index_screener(timeframe = 14, upperbound = 0.8, lowerbound = 0.2):
	"""
	Stochastic Relative Strength Index screener
	Keyword Arguments (set by user during runtime):
		timeframe: Sets the timeframe (number of trading sessions) (daily) for Stochastic RSI screen. Supported values are between 2 and 97 (inclusive) atm.
		upperbound: Sets the stochrsi value such that any stock with stochrsi >= upperbound is considered overbought. Supported values are between 0.7 and 1 (inclusive).
		lowerbound: Sets the stochrsi value such that any stock with stochrsi <= lowerbound is considered oversold. Supported values are between 0 and 0.3 (inclusive).
	"""

	print("\n\n----------STOCHASTIC RSI SCREEN----------\n\n")
	time.sleep(0.1)
	print("----------SETTINGS----------\n\n")
	time.sleep(0.1)

	print("TIMEFRAME: " + str(timeframe) + "\n\n")
	time.sleep(0.1)
	print("OVERBOUGHT AT OR ABOVE: " + str(upperbound) + "\n\n")
	time.sleep(0.1)
	print("OVERSOLD AT OR BELOW: " + str(lowerbound) + "\n\n")
	time.sleep(0.1)
	print("SCREENING......\n\n")
	time.sleep(0.1)

	stochrsi_overbought = {}
	stochrsi_oversold = {}
	stochrsi_neutral = {}

	for company_name, company_ticker in sti_stocks.items():
		company_name_no_spaces = company_name.replace(" ", "_")

		#Load stock's csv file with date as index
		df_original = pd.read_csv("sti_stock_data/original_data/" + company_name_no_spaces + ".csv", index_col = ["date"])

		#Get stock's adjusted close series (previous 100 trading sessions)
		df_rsi = df_original[["5. adjusted close"]]

		#Calculate stock's daily adjusted close changes
		df_rsi["daily_price_change"] = df_rsi["5. adjusted close"].diff(periods = -1)

		#Remove last row due which has NaN value
		df_rsi = df_rsi[:-1]	

		#Reverse dataframe
		df_rsi.sort_values(by = ["date"], inplace = True)

		#Get two copies of daily_price_change dataframe for filtering values
		df_rsi_up = df_rsi["daily_price_change"]
		df_rsi_down = df_rsi["daily_price_change"]

		#Filter the gains and losses in each copy
		df_rsi_up = df_rsi_up.apply(lambda x: 0 if x < 0 else x)
		df_rsi_down = df_rsi_down.apply(lambda x: 0 if x > 0 else x)

		#Merge dataframes
		df_rsi["daily_price_increase"] = df_rsi_up
		df_rsi["daily_price_decrease"] = df_rsi_down

		#Calculate average gain and loss over the specified timeframe
		df_rsi_up_rolling_mean = df_rsi_up.rolling(window = timeframe).mean()
		df_rsi_down_rolling_mean = df_rsi_down.abs().rolling(window = timeframe).mean()

		#Merge into main fataframe
		df_rsi["daily_price_increase_rolling_mean"] = df_rsi_up_rolling_mean
		df_rsi["daily_price_decrease_rolling_mean"] = df_rsi_down_rolling_mean

		#Remove first (timeframe - 1) rows which have NaN values
		df_rsi = df_rsi[timeframe - 1:]

		#Get subset of dataframe depending on the timeframe
		df_rsi = df_rsi[-timeframe:]

		#Shift daily_price_increase_rolling_mean and daily_price_decrease_rolling_mean columns down by 1 row for rest of relative strength calculations
		df_rsi["daily_price_increase_rolling_mean_calc"] = df_rsi["daily_price_increase_rolling_mean"].shift(1)
		df_rsi["daily_price_decrease_rolling_mean_calc"] = df_rsi["daily_price_decrease_rolling_mean"].shift(1)

		#Calculate average price increase / decrease for rest of the rows
		df_rsi["daily_price_average_increase"] = ((df_rsi["daily_price_increase_rolling_mean_calc"] * (timeframe - 1)) + df_rsi["daily_price_increase"]) / timeframe
		df_rsi["daily_price_average_decrease"] = ((df_rsi["daily_price_decrease_rolling_mean_calc"] * (timeframe - 1)) + df_rsi["daily_price_decrease"]) / timeframe

		#Calculate average price increase / decrease for first row
		df_rsi.iloc[0, 8] = df_rsi.iloc[0, 4] / timeframe
		df_rsi.iloc[0, 9] = df_rsi.iloc[0, 5] / timeframe

		#Calculate relative strength
		df_rsi["relative_strength"] = df_rsi["daily_price_average_increase"] / df_rsi["daily_price_average_decrease"]

		#Calculate relative strength index
		df_rsi["relative_strength_index"] = 100 - (100 / (1 + df_rsi["relative_strength"]))

		#Convert to two decimal places
		df_rsi["relative_strength_index"] = df_rsi["relative_strength_index"].round(decimals = 2)

		#Get subset of dataframe with only relative strength index values for the timeframe set
		df_rsi_calc = df_rsi[["relative_strength_index"]]

		#Get the current day's rsi value
		rsi = df_rsi_calc["relative_strength_index"][-1]

		#Get the highest and lowest relative strength index values in the timeframe set
		df_rsi_calc_max = max(df_rsi_calc["relative_strength_index"])
		df_rsi_calc_min = min(df_rsi_calc["relative_strength_index"])

		#Calculate stochastic relative strength index
		stochastic_rsi = (rsi - df_rsi_calc_min) / (df_rsi_calc_max - df_rsi_calc_min)

		#Convert stochastic relative strength index value to two decimal places
		stochastic_rsi = round(decimal.Decimal(stochastic_rsi), 2)

		#Classify stochastic relative strength index values
		if stochastic_rsi >= upperbound:
			stochrsi_overbought[company_name] = stochastic_rsi
		elif stochastic_rsi <= lowerbound:
			stochrsi_oversold[company_name] = stochastic_rsi
		else:
			stochrsi_neutral[company_name] = stochastic_rsi

	#Sort results
	stochrsi_overbought_sorted = sorted(stochrsi_overbought.items(), key = lambda x: x[1], reverse = True)
	stochrsi_neutral_sorted = sorted(stochrsi_neutral.items(), key = lambda x: x[1], reverse = True)
	stochrsi_oversold_sorted = sorted(stochrsi_oversold.items(), key = lambda x: x[1])

	print("----------STOCHASTIC RSI SCREEN RESULTS----------\n\n")
	time.sleep(0.1)
	print("-----OVERBOUGHT-----\n\n")
	time.sleep(0.1)

	df_stochrsi_overbought_sorted = pd.DataFrame(stochrsi_overbought_sorted, columns = ["Company", "Stochastic Relative Strength Index"])
	pprint(df_stochrsi_overbought_sorted)

	print("\n\n-----NEUTRAL-----\n\n")
	time.sleep(0.1)

	df_stochrsi_neutral_sorted = pd.DataFrame(stochrsi_neutral_sorted, columns = ["Company", "Stochastic Relative Strength Index"])
	pprint(df_stochrsi_neutral_sorted)

	print("\n\n-----OVERSOLD-----\n\n")
	time.sleep(0.1)

	df_stochrsi_oversold_sorted = pd.DataFrame(stochrsi_oversold_sorted, columns = ["Company", "Stochastic Relative Strength Index"])
	pprint(df_stochrsi_oversold_sorted)

	print("\n\n--------------------\n\n")

	technical_analysis_menu()


if __name__ == "__main__":
	initialize()
	wrangle_data()
	combine_data()
	price_volume_top_pct_change_screener(screen = "price", timeframe = "daily")
	price_volume_top_pct_change_screener(screen = "price", timeframe = "weekly")
	price_volume_top_pct_change_screener(screen = "price", timeframe = "monthly")
	price_volume_top_pct_change_screener(screen = "volume", timeframe = "daily")
	price_volume_top_pct_change_screener(screen = "volume", timeframe = "weekly")
	price_volume_top_pct_change_screener(screen = "volume", timeframe = "monthly")
	technical_analysis_menu()
	time.sleep(10000)
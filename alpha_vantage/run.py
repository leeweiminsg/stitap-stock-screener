import time
import decimal
import json
import pandas as pd
import numpy as np
from pprint import pprint
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

sti_stocks = {"CityDev":"C09.SI", "DBS":"D05.SI", "UOL":"U14.SI", "SingTel":"Z74.SI", "UOB":"U11.SI",
				"Keppel Corp":"BN4.SI", "CapitaLand":"C31.SI", "OCBC Bank":"O39.SI", "Genting Sing":"G13.SI", "Venture":"V03.SI",
				"CapitaMall Trust":"C38U.SI", "YZJ Shipbldg SGD":"BS6.SI", "CapitaCom Trust":"C61U.SI", "Ascendas Reit":"A17U.SI", "ComfortDelGro":"C52.SI",
				"SIA":"C6L.SI", "Jardine C&C":"C07.SI", "SPH":"T39.SI", "SGX":"S68.SI", "ThaiBev":"Y92.SI",
				"ST Engineering":"S63.SI", "Sembcorp Ind":"U96.SI", "Wilmar Intl":"F34.SI", "StarHub":"CC3.SI", "SATS":"S58.SI",
				"HongkongLand USD":"H78.SI", "JSH USD":"J37.SI", "JMH USD":"J36.SI", "HPH Trust USD":"NS8U.SI", "Golden Agri-Res":"E5H.SI"}


def main():
	"""
	Loops over each of the component stocks (30 of them) in the Straits Times Index, displaying information about their daily (adjusted) prices.

	REQUIRES: API KEY (you can get them for free on AlphaVantage's website)

	INSTRUCTIONS:
	Set the key argument to your own unique API key value.
	AlphaVantage limits API calls, so the program will take around 10mins to finish executing per run.
	Original stock market data will be stored at sti_stock_data/original data.
	
	ts = TimeSeries(key = "PKJT2CWR5IH8QHVS", output_format = "pandas") # <--- SET API KEY HERE

	ti = TechIndicators()"""


def initialize():
	"""Initializes the program by fetching and storing data"""

	ts = TimeSeries(key = "", output_format = "pandas") # <--- SET API KEY HERE

	print("-----Straits Times Index Technical Analysis Project: STITAP-----\n\n\n")
	time.sleep(0.1)

	print("-----V1.0.0-----\n\n\n")
	time.sleep(0.1)

	print("INITIALIZING: LOADING AND SAVING ALL 30 STI STOCK DATA:\n\n")
	time.sleep(0.1)

	for company_name, company_ticker in sti_stocks.items():
		time.sleep(0.1)
		print ("LOADING: " + company_name + " " + company_ticker + "\n")
		company_name_no_spaces = company_name.replace(" ", "_")
		time.sleep(60) # <--- Adjust the duration (No. of seconds) of waiting time between each API call here
		
		#Makes API call
		data, meta_data  = ts.get_daily_adjusted(symbol = company_ticker)

		#Sorts the resulting data pandas object in order of recency (latest date on top)
		data.sort_index(ascending = False, inplace = True)
		
		#Stores the csv file to sti_stock_data/original_data
		data.to_csv("sti_stock_data/original_data/" + company_name_no_spaces + ".csv", mode = "w")
		
		print ("\nLOADED AND SAVED: " + company_name + "\n\n")

	print("INITIALIZED: ALL 30 STI STOCK DATA LOADED AND SAVED\n\n")
	print("---------------------------------------------------------------\n\n")


def wrangle_data():

	print("WRANGLING AND SAVING DATA:\n\n")

	for company_name, company_ticker in sti_stocks.items():
		time.sleep(0.1)
		company_name_no_spaces = company_name.replace(" ", "_")
		print ("WRANGLING AND SAVING DATA: " + company_name + " " + company_ticker + "\n")
		df_original = pd.read_csv("sti_stock_data/original_data/" + company_name_no_spaces + ".csv")

		#Retrieve dates (CAUTION: ESTIMATED VALUES)
		most_recent_date = df_original.iloc[0, 0]
		one_day_before_date = df_original.iloc[1, 0]	
		one_week_before_date = df_original.iloc[5, 0]	#One week consists of roughly 5 trading days   (NOT EXACT)
		one_month_before_date = df_original.iloc[20, 0] #One month consists of roughly 20 trading days (NOT EXACT)

		#Retrieve prices (we use adjusted closing prices)
		most_recent_price = df_original.iloc[0, 5]
		one_day_before_price = df_original.iloc[1, 5]
		one_week_before_price = df_original.iloc[5, 5]
		one_month_before_price = df_original.iloc[20, 5]

		#Retrive volume
		most_recent_volume = df_original.iloc[0, 6]
		one_day_before_volume = df_original.iloc[1, 6]
		one_week_before_volume = df_original.iloc[5, 6]
		one_month_before_volume = df_original.iloc[20, 6]

		#Calculate price changes (again we use adjusted closing prices here)
		one_day_price_change = most_recent_price - one_day_before_price
		one_week_price_change = most_recent_price - one_week_before_price
		one_month_price_change = most_recent_price - one_month_before_price

		#Calculate price changes in percentage terms (again we use adjusted closing prices here)
		one_day_price_change_pct = (one_day_price_change / one_day_before_price) * 100
		one_week_price_change_pct = (one_week_price_change / one_week_before_price) * 100
		one_month_price_change_pct = (one_month_price_change / one_month_before_price) * 100

		#Calculate volume changes
		one_day_volume_change = most_recent_volume - one_day_before_volume
		one_week_volume_change = most_recent_volume - one_week_before_volume
		one_month_volume_change = most_recent_volume - one_month_before_volume

		#Calculate volume changes in percentage terms
		one_day_volume_change_pct = (one_day_volume_change / one_day_before_volume) * 100
		one_week_volume_change_pct = (one_week_volume_change / one_week_before_volume) * 100
		one_month_volume_change_pct = (one_month_volume_change / one_month_before_volume) * 100

		#This dictionary contains all the basic price and volume information for an individual stock
		simple_price_volume_changes = {"company_name_no_spaces":company_name_no_spaces,
									   "most_recent_date":most_recent_date, "one_day_before_date":one_day_before_date,
									   "one_week_before_date":one_week_before_date, "one_month_before_date":one_month_before_date,
									   "most_recent_price":most_recent_price, "one_day_before_price":one_day_before_price,
									   "one_week_before_price":one_week_before_price, "one_month_before_price":one_month_before_price,
									   "most_recent_volume":most_recent_volume, "one_day_before_volume":one_day_before_volume,
									   "one_week_before_volume":one_week_before_volume, "one_month_before_volume":one_month_before_volume,
									   "one_day_price_change":one_day_price_change, "one_week_price_change":one_week_price_change,
									   "one_month_price_change":one_month_price_change, "one_day_price_change_pct":one_day_price_change_pct,
									   "one_week_price_change_pct":one_week_price_change_pct, "one_month_price_change_pct":one_month_price_change_pct,
									   "one_day_volume_change":one_day_volume_change, "one_week_volume_change":one_week_volume_change,
									   "one_month_volume_change":one_month_volume_change, "one_day_volume_change_pct":one_day_volume_change_pct,
									   "one_week_volume_change_pct":one_week_volume_change_pct, "one_month_volume_change_pct":one_month_volume_change_pct}

		#Converts the simple_price_volume_changes dictionary to a pandas series
		df_simple_price_volume_changes = pd.DataFrame([simple_price_volume_changes])
		df_simple_price_volume_changes.set_index(["company_name_no_spaces"], inplace = True)

		#Converts the df_simple_price_volume_changes pandas series to csv and stores the csv file to sti_stock_data/wrangled_data
		df_simple_price_volume_changes.to_csv("sti_stock_data/wrangled_data/" + company_name_no_spaces + "_wrangled.csv", mode = "w")

		print ("\nWRANGLED DATA AND SAVED: " + company_name + "\n\n")
	
	print("PREPARED: ALL 30 STI STOCK DATA WRANGLED AND RESULTS SAVED\n\n")
	print("---------------------------------------------------------------\n\n")


def combine_data():

	print("COMBINING DATA:\n\n")

	df_simple_price_volume_changes_main = pd.DataFrame()

	for company_name, company_ticker in sti_stocks.items():
		company_name_no_spaces = company_name.replace(" ", "_")

		#Read csv file and organise the data
		df_simple_price_volume_changes = pd.read_csv("sti_stock_data/wrangled_data/" + company_name_no_spaces + "_wrangled.csv", index_col = 0)
		df_simple_price_volume_changes_main = pd.concat([df_simple_price_volume_changes_main, df_simple_price_volume_changes])

	df_simple_price_volume_changes_main.to_csv("sti_stock_data/combined_data/combined_data.csv", mode = "w")
	pd.set_option("display.max_columns", 30)
	
	print("COMBINED: ALL WRANGLED DATA COMBINED AND RESULTS SAVED\n\n")
	print("---------------------------------------------------------------\n\n")


def top_changes_price_volume_screener(screen = "price", timeframe = "day"):
	"""
	Keyword arguments:
		screen: type of stock screen, supported values are: "price"
			"price": filters top and bottom 5 stocks of the Straits Times Index in terms of percentage price changes
			"volume": filters top and bottom 5 stocks of the Straits Times Index in terms of percentage volume changes
		timeframe: sets the timeframe for the screen, supported values are: "day", "week", "month"
			"day": timeframe set to 1 day
			"week": timeframe set to 1 week
			"month": timeframe set to 1 month
	"""

	#Filter stocks for top 5 price or volume increases and declines of the Straits Times Index depending on the timeframe set
	df_simple_price_volume_changes_main = pd.read_csv("sti_stock_data/combined_data/combined_data.csv")

	print("TOP 5 STI STOCKS WITH HIGHEST PERCENTAGE CHANGE IN " + screen.upper() + ": (BY " + timeframe.upper() + ")\n\n")
	print("---------------------\n\n")
	df_timeframe_change_pct_top_five = df_simple_price_volume_changes_main.nlargest(5, "one_" + timeframe +"_" + screen + "_change_pct")
	df_timeframe_change_pct_top_five = df_timeframe_change_pct_top_five[["company_name_no_spaces", "one_" + timeframe +"_" + screen + "_change_pct"]]
	pprint(df_timeframe_change_pct_top_five)
	print("\n\n---------------------\n\n")

	print("TOP 5 STI STOCKS WITH LOWEST PERCENTAGE CHANGE IN " + screen.upper() + ": (BY " + timeframe.upper() + ")\n\n")
	print("---------------------\n\n")
	df_timeframe_change_pct_bottom_five = df_simple_price_volume_changes_main.nsmallest(5, "one_" + timeframe +"_" + screen + "_change_pct")
	df_timeframe_change_pct_bottom_five = df_timeframe_change_pct_bottom_five[["company_name_no_spaces", "one_" + timeframe +"_" + screen + "_change_pct"]]
	pprint(df_timeframe_change_pct_bottom_five)
	print("\n\n---------------------\n\n")


def technical_analysis_menu():
	"""
	Displays menu for technical screen.
	Requires user input.
	"""

	print("----------STI TECHNICAL ANALYSIS SCREENER----------\n\n")
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

	print("SETTINGS FOR " + screen + ":")


	if screen == "STOCHRSI":

		timeframe_i = validate_input("Please enter your desired timeframe:", input_type = int, input_range = range(2, 50))
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

		timeframe_i = validate_input("Please enter your desired timeframe:", input_type = int, input_range = range(2, 100))
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
		timeframe: Sets the timeframe (number of trading sessions) (daily) for RSI screen. Supported values are between 2 and 100 (inclusive) atm.
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

		#Read csv file
		df_original = pd.read_csv("sti_stock_data/original_data/" + company_name_no_spaces + ".csv", index_col = 0)

		#Prepare pandas series for calculations
		df_technical_timeframe = df_original.head(timeframe + 1)
		df_technical_timeframe_adjusted_close = df_technical_timeframe["5. adjusted close"]
		
		#Calculate daily price changes
		df_technical_timeframe_price_change = df_technical_timeframe_adjusted_close.diff(periods = -1)
		
		#Remove last row which has NA value
		df_technical_timeframe_price_change_cleaned = df_technical_timeframe_price_change[:-1]
		
		#Prepare two pandas series: one only for price increases and another for declines
		df_technical_timeframe_price_change_cleaned_up = df_technical_timeframe_price_change_cleaned.copy()
		df_technical_timeframe_price_change_cleaned_down = df_technical_timeframe_price_change_cleaned.copy()

		df_technical_timeframe_price_change_cleaned_up[df_technical_timeframe_price_change_cleaned_up < 0] = 0
		df_technical_timeframe_price_change_cleaned_down[df_technical_timeframe_price_change_cleaned_down > 0] = 0

		#Calculate average gain and loss over the specified timeframe
		df_technical_timeframe_price_change_cleaned_up_rolling_mean = df_technical_timeframe_price_change_cleaned_up.rolling(timeframe).mean()[-1]
		df_technical_timeframe_price_change_cleaned_down_rolling_mean = df_technical_timeframe_price_change_cleaned_down.abs().rolling(timeframe).mean()[-1]
		
		rsi_timeframe_relative_strength = df_technical_timeframe_price_change_cleaned_up_rolling_mean / df_technical_timeframe_price_change_cleaned_down_rolling_mean

		rsi_timeframe = 100 - (100 / (1 + rsi_timeframe_relative_strength))

		rsi_timeframe_decimal = round(decimal.Decimal(rsi_timeframe), 2)

		if rsi_timeframe_decimal >= upperbound:
			rsi_overbought[company_name] = rsi_timeframe_decimal
		elif rsi_timeframe_decimal <= lowerbound:
			rsi_oversold[company_name] = rsi_timeframe_decimal
		else:
			rsi_neutral[company_name] = rsi_timeframe_decimal

	#Sort results
	rsi_overbought_sorted = sorted(rsi_overbought.items(), key = lambda x: x[1], reverse = True)
	rsi_neutral_sorted = sorted(rsi_neutral.items(), key = lambda x: x[1], reverse = True)
	rsi_oversold_sorted = sorted(rsi_oversold.items(), key = lambda x: x[1])

	print("----------RSI SCREEN RESULTS----------\n\n")
	time.sleep(0.1)
	print("-----OVERBOUGHT-----\n\n")
	time.sleep(0.1)

	df_rsi_overbought_sorted = pd.DataFrame(rsi_overbought_sorted, columns = ["Company", "Relative Strength Index"])
	pprint(df_rsi_overbought_sorted)

	print("\n\n-----NEUTRAL-----\n\n")
	time.sleep(0.1)

	df_rsi_neutral_sorted = pd.DataFrame(rsi_neutral_sorted, columns = ["Company", "Relative Strength Index"])
	pprint(df_rsi_neutral_sorted)

	print("\n\n-----OVERSOLD-----\n\n")
	time.sleep(0.1)

	df_rsi_oversold_sorted = pd.DataFrame(rsi_oversold_sorted, columns = ["Company", "Relative Strength Index"])
	pprint(df_rsi_oversold_sorted)

	print("\n\n--------------------\n\n")

	technical_analysis_menu()


def stochastic_relative_strength_index_screener(timeframe = 14, upperbound = 0.8, lowerbound = 0.2):
	"""
	Stochastic Relative Strength Index screener
	Keyword Arguments (set by user during runtime):
		timeframe: Sets the timeframe (number of trading sessions) (daily) for Stochastic RSI screen. Supported values are between 2 and 49 (inclusive) atm.
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
		company_rsi_timeframe = []

		#Read csv file
		df_original = pd.read_csv("sti_stock_data/original_data/" + company_name_no_spaces + ".csv", index_col = 0)

		#Prepare pandas series for calculations
		df_technical_timeframe = df_original.head(timeframe + timeframe)
		df_technical_timeframe_adjusted_close = df_technical_timeframe["5. adjusted close"]
		
		#Calculate daily price changes
		df_technical_timeframe_price_change = df_technical_timeframe_adjusted_close.diff(periods = -1)
		
		#Remove last row which has NA value
		df_technical_timeframe_price_change_cleaned = df_technical_timeframe_price_change[:-1]

		for i in range(0, 14):
			df_technical_timeframe_price_change_cleaned_temp = df_technical_timeframe_price_change_cleaned[i:(i + timeframe)]
			
			#Prepare two pandas series: one only for price increases and another for declines
			df_technical_timeframe_price_change_cleaned_up = df_technical_timeframe_price_change_cleaned_temp.copy()
			df_technical_timeframe_price_change_cleaned_down = df_technical_timeframe_price_change_cleaned_temp.copy()

			df_technical_timeframe_price_change_cleaned_up[df_technical_timeframe_price_change_cleaned_up < 0] = 0
			df_technical_timeframe_price_change_cleaned_down[df_technical_timeframe_price_change_cleaned_down > 0] = 0

			#Calculate average gain and loss over the specified timeframe
			df_technical_timeframe_price_change_cleaned_up_rolling_mean = df_technical_timeframe_price_change_cleaned_up.rolling(timeframe).mean()[-1]
			df_technical_timeframe_price_change_cleaned_down_rolling_mean = df_technical_timeframe_price_change_cleaned_down.abs().rolling(timeframe).mean()[-1]
			
			rsi_timeframe_relative_strength = df_technical_timeframe_price_change_cleaned_up_rolling_mean / df_technical_timeframe_price_change_cleaned_down_rolling_mean

			rsi_timeframe = 100 - (100 / (1 + rsi_timeframe_relative_strength))

			#Add daily rsi value to list
			company_rsi_timeframe.append(rsi_timeframe)

		#Calculate stochastic rsi using daily rsi values in list
		company_rsi_timeframe_current = company_rsi_timeframe[0]
		company_rsi_timeframe_max = max(company_rsi_timeframe)
		company_rsi_timeframe_min = min(company_rsi_timeframe)

		stochastic_rsi = (company_rsi_timeframe_current - company_rsi_timeframe_min) / (company_rsi_timeframe_max - company_rsi_timeframe_min)

		stochastic_rsi_decimal = round(decimal.Decimal(stochastic_rsi), 2)

		if stochastic_rsi_decimal >= upperbound:
			stochrsi_overbought[company_name] = stochastic_rsi_decimal
		elif stochastic_rsi_decimal <= lowerbound:
			stochrsi_oversold[company_name] = stochastic_rsi_decimal
		else:
			stochrsi_neutral[company_name] = stochastic_rsi_decimal

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
	top_changes_price_volume_screener(screen = "price", timeframe = "day")
	top_changes_price_volume_screener(screen = "price", timeframe = "week")
	top_changes_price_volume_screener(screen = "price", timeframe = "month")
	top_changes_price_volume_screener(screen = "volume", timeframe = "day")
	top_changes_price_volume_screener(screen = "volume", timeframe = "week")
	top_changes_price_volume_screener(screen = "volume", timeframe = "month")
	technical_analysis_menu()
	time.sleep(10000)

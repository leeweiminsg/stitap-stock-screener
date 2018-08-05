from run import initialize, sti_tickers

def backtest_menu():
	"""
	Displays menu for backtests.
	Requires user input.
	"""

	timeframe_input_dict = {
							1:"daily",
							2:"weekly",
							3:"monthly"
							}

	print("----------STITAP TECHNICAL ANALYSIS BACKTEST----------", end = "\n"*3)
	time.sleep(0.1)

	print("Please enter your desired timeframe for backtesting (eg. type 1 for daily timeframe) :", end = "\n"*3)
	time.sleep(0.1)
	
	while True:

		timeframe = input("""
						1 - daily
						2 - weekly
						3 - monthly
						""")

		if int(timeframe) in timeframe_input_dict:
			time.sleep(0.1)
			print("\n"*3)
			print(f"{timeframe_input_dict[timeframe]} TIMEFRAME SELECTED", end = "\n"*3)
			time.sleep(0.1)
			break

		else:
			print("\n"*3)
			print("Invalid input. Please try again.", end = "\n"*3)

	initialize(backtest = timeframe_input_dict[timeframe])
	backtest_plot_menu()

def backtest_plot_menu():
	"""
	Displays menu for backtest actions.
	Requires user input.
	Currently only historical stock price plots are supported.
	"""

	company_ticker_dict = {
						1:"CityDev", 2:"DBS", 3:"UOL", 4:"SingTel", 5:"UOB",
						6:"Keppel Corp", 7:"CapitaLand", 8:"OCBC Bank", 9:"Genting Sing", 10:"Venture",
						11:"CapitaMall Trust", 12:"YZJ Shipbldg SGD", 13:"CapitaCom Trust", 14:"Ascendas Reit", 15:"ComfortDelGro",
						16:"SIA", 17:"Jardine C&C", 18:"SPH", 19:"SGX", 20:"ThaiBev",
						21:"ST Engineering", 22:"Sembcorp Ind", 23:"Wilmar Intl", 24:"StarHub", 25:"SATS",
						26:"HongkongLand USD", 27:"JSH USD", 28:"JMH USD", 29:"HPH Trust USD", 30:"Golden Agri-Res"
						}

	print("Please enter your desired stock for backtesting (eg. type 1 for CityDev stock) :", end = "\n"*3)
	time.sleep(0.1)

	while True:

		company_ticker = input()

		if company_ticker in company_ticker_dict:
			time.sleep(0.1)
			print("\n"*3)
			print(f"{company_ticker_dict[company_ticker]} SELECTED", end = "\n"*3)
			time.sleep(0.1)
			print(f"PLOTTING PRICE CHART FOR {company_ticker_dict[company_ticker]}:", end = "\n"*3)
			break

		else:
			print("\n"*3)
			print("Invalid input. Please try again.", end = "\n"*3)


if __name__ == "__main__":
	backtest_menu()
	
	time.sleep(10000)
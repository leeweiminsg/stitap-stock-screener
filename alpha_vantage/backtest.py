from run import initialize

if __name__ == "__main__":
	initialize(backtest = 'daily')
	initialize(backtest = 'weekly')
	initialize(backtest = 'monthly')
	
	time.sleep(10000)
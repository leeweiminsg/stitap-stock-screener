from abc import ABC, abstractmethod
from pprint import pprint

import pandas as pd

class TopPctChangeScreen(ABC):
	"""Abstract base class for screening stocks with top n percentage change in an attribute (in a timeframe)
	"""
	def __init__(self, timeframe="daily", n=5, timeframes=["daily", "weekly", "monthly"]):
		"""
		Keyword Arguments:
			timeframe: timeframe of screen. Supported values are "daily", "weekly" and "monthly" (default "daily")
			n: number of stocks to screen for. (default n)
		"""
		self._timeframe = timeframe
		self._n = n
		self._timeframes = timeframes

	@property
	def timeframe(self):
		return self._timeframe

	@timeframe.setter
	def timeframe(self, timeframe):
		self._timeframe = timeframe

	@property
	def n(self):
		return self._n

	@n.setter
	def n(self, n):
		self._n = n

	def input(self):
		"""Collects data
		"""
		self._df_combined = pd.read_csv("sti_stock_data/combined_data/combined_data.csv")

	@abstractmethod
	def top_pct_change(self):
		"""Screens stocks with top n percentage change in an attribute
		"""
		pass

	def summarize(self):
		"""Runs top_pct_change for each timeframe, summarizing the results

		Keyword Arguments:
			timeframes: list of timeframes for running top_pct_change
		"""
		for timeframe in self._timeframes:
			self.timeframe = timeframe
			self.top_pct_change()

	def run(self):
		"""Runs the screen
		"""
		self.input()
		self.summarize()


class TopPricePctChangeScreen(TopPctChangeScreen):
	"""Screens stocks with top n percentage change in price (in a timeframe)
	"""
	def top_pct_change(self):
		"""Screens stocks with top n percentage change in price
		"""
		print(f"TOP {self.n} STOCKS WITH HIGHEST PERCENTAGE CHANGE IN PRICE: {self.timeframe.upper()} SCREEN", end="\n"*2)
		print("-"*20, end="\n"*2)
		top_n = self._df_combined.nlargest(n=self.n, columns=f"price_{self.timeframe}_pct_change")
		top_n = top_n[["stock_name_no_spaces", f"price_{self.timeframe}_pct_change"]]
		pprint(top_n)
		print("-"*20, end="\n"*2)

		print(f"TOP {self.n} STOCKS WITH LOWEST PERCENTAGE CHANGE IN PRICE: {self.timeframe.upper()} SCREEN", end="\n"*2)
		print("-"*20, end="\n"*2)
		bottom_n = self._df_combined.nsmallest(n=self.n, columns=f"price_{self.timeframe}_pct_change")
		bottom_n = bottom_n[["stock_name_no_spaces", f"price_{self.timeframe}_pct_change"]]
		pprint(bottom_n)
		print("-"*20, end="\n"*2)


class TopVolumePctChangeScreen(TopPctChangeScreen):
	"""Screens stocks with top n percentage change in volume (in a timeframe)
	"""
	def top_pct_change(self):
		"""Screens stocks with top n percentage change in volume
		"""
		print(f"TOP {self.n} STOCKS WITH HIGHEST PERCENTAGE CHANGE IN VOLUME: {self.timeframe.upper()} SCREEN", end="\n"*2)
		print("-"*20, end="\n"*2)
		top_n = self._df_combined.nlargest(n=self.n, columns=f"volume_{self.timeframe}_pct_change")
		top_n = top_n[["stock_name_no_spaces", f"volume_{self.timeframe}_pct_change"]]
		pprint(top_n)
		print("-"*20, end="\n"*2)

		print(f"TOP {self.n} STOCKS WITH LOWEST PERCENTAGE CHANGE IN VOLUME: {self.timeframe.upper()} SCREEN", end="\n"*2)
		print("-"*20, end="\n"*2)
		bottom_n = self._df_combined.nsmallest(n=self.n, columns=f"volume_{self.timeframe}_pct_change")
		bottom_n = bottom_n[["stock_name_no_spaces", f"volume_{self.timeframe}_pct_change"]]
		pprint(bottom_n)
		print("-"*20, end="\n"*2)
import save_tickr_data
import InsiderScraping
import numpy as np

def LookAheadPL(ticker_prices, dob, look_ahead = 3):
	#ticker prices should be self explanatory
	#dob is the date the insider bought the stock
	#look_ahead is the number of days to hold before selling
	for i in range(0, len(ticker_prices)):
		target_dataframe = ticker_prices.iloc[i, 0]
		if target_dataframe == dob:
			return ((ticker_prices.iloc[i+1+look_ahead, 4]-ticker_prices.iloc[i+1, 1])/ticker_prices.iloc[i+1, 1])


tickers_and_dates = InsiderScraping.GetInsiderData()
last_ticker = ""
running = 0
num_so_far = 1

for tad in tickers_and_dates:
	if tad[1] != last_ticker:
		try:
			this_ticker = save_tickr_data.DownAndLoadData(tad[1], wod = "d")
		except:
			print("this stock might not exist")


		try:
			perc = LookAheadPL(this_ticker, tad[0])
			running += perc
			print(tad[1], perc, running/num_so_far)
		except:
			print("too recent")

		last_ticker = tad[1]
		num_so_far += 1

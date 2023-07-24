import save_tickr_data
import InsiderScraping
import numpy as np
import time
import datetime
import matplotlib.pyplot as plt

stop_loss = 0.1
#sell_early = 0.15
start_cash = 1000

def LookAheadPL(ticker_prices, dob, look_ahead = 3):
	#something is wrong here and im sleepy
	#ticker prices should be self explanatory
	#dob is the date the insider bought the stock
	#look_ahead is the number of days to hold before selling
	for i in range(0, len(ticker_prices)):
		target_dataframe = ticker_prices.iloc[i, 0]
		if target_dataframe == dob:
			#indexing 3 is low, 4 for close
			return ((ticker_prices.iloc[i+1+look_ahead, 3]-ticker_prices.iloc[i+1, 1])/ticker_prices.iloc[i+1, 1])


tickers_and_dates = InsiderScraping.GetInsiderData()
dates_dict = {}
last_date = ''
for tad in tickers_and_dates:
	dates_dict[tad[0]] = []

for tad in tickers_and_dates:
	if tad[1] not in dates_dict[tad[0]]:
		dates_dict[tad[0]].append(tad[1])

all_unix_dates = []
for i in dates_dict:
	tim = int(time.mktime(datetime.datetime.strptime(i, "%Y-%m-%d").timetuple()))
	all_unix_dates.append(tim)

all_unix_dates.sort()

all_keys_sorted = []
for tim in all_unix_dates:
	all_keys_sorted.append(str(datetime.datetime.fromtimestamp(tim).strftime('%Y-%m-%d')))

cash = start_cash
Ts = []
Cs = []
t = 0
for tim in all_keys_sorted:
	t += 1
	stocks = dates_dict[tim]
	perc_move = 0 
	stock_used = 0
	for s in stocks:
		try:
			this_ticker = save_tickr_data.DownAndLoadData(s, wod = "d")
		except:
			pass

		try:
			perc_move += LookAheadPL(this_ticker, tim)
			stock_used += 1
		except:
			pass

		try:
			perc_move /= stock_used
			perc_move += 1
		except:
			perc_move = 1
		
		
	cash = cash*2/3 + cash*perc_move/3 #only one third of cash per day
	Ts.append(t)
	Cs.append(cash)
	print(tim, cash, perc_move, stock_used)

print(Cs)
print(Ts)
plt.plot(Ts, Cs)
plt.show()



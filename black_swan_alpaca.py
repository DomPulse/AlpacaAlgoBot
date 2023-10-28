from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
import requests
import csv
import pandas
import numpy as np
import matplotlib.pyplot as plt
import webbrowser
import time
import datetime
from bs4 import BeautifulSoup
import InsiderScraping

#incorporate seeing when these people sell into the strategy

key = 'PK6CWILOP2WI5ND55D7O'
secret_key = 'q3WtU8Q6lmmjQhgmcxFCIgEWbZNKL41lmVo1XUCq'
base_url = 'https://paper-api.alpaca.markets'

trading_client = TradingClient(key, secret_key, paper=True)

api = tradeapi.REST(key, secret_key, base_url, api_version='v2')

# Get our account information.
account = trading_client.get_account()

# Check if our account is restricted from trading.
if account.trading_blocked:
	print('Account is currently restricted from trading.')

all_money = account.buying_power
sec_in_day = 24*60*60

def PlaceOrder(ticker, qty, side = "buy"):
	print(qty)
	if side == "buy":
		market_order_data = MarketOrderRequest(
						symbol=ticker,
						qty=qty,
						side=OrderSide.BUY,
						time_in_force=TimeInForce.DAY
						)
	elif side == "sell":
		market_order_data = MarketOrderRequest(
						symbol=ticker,
						qty=qty,
						side=OrderSide.SELL,
						time_in_force=TimeInForce.DAY)
	else:
		print("invalid order")
		return 0

	market_order = trading_client.submit_order(order_data=market_order_data)

def rebalance(should_be_bought, already_bought):
	print(already_bought)
	#i finish tomorrow
	total_cash_money_honey = float(account.buying_power) #need to get the money and assets but yeah whatever
	open_positions = api.list_positions()
	for position in open_positions:
		#maybe unnecessay?
		latest_trade = api.get_latest_trade(position.symbol)
		current_price = latest_trade.price
		total_cash_money_honey += float(current_price)*float(position.qty)

	for ticker in should_be_bought:
		latest_trade = api.get_latest_trade(ticker)
		des_qty = total_cash_money_honey/(1.2*float(latest_trade.price)*len(should_be_bought))

		try:
			current_qty = float(already_bought[ticker])
		except:
			current_qty = 0

		if des_qty > current_qty:
			PlaceOrder(ticker, des_qty - current_qty, "buy")
		elif des_qty < current_qty:
			PlaceOrder(ticker, current_qty - des_qty, "sell")
		else:
			pass



	return 0

def BuyAndSell():
	day_of_week = datetime.datetime.now().weekday()
	potential_stocks = ['AKAM', 'ALK', 'ALB', 'ALGN', 'AMZN', 'AMD', 'AIG', 'APA', 'ADSK', 'AXON', 'BKR', 'BAC', 'BBWI', 'BBY', 'BKNG', 'BWA', 'COF', 'KMX', 'CCL', 'CBRE', 'CNC', 'CRL', 'C', 'CMA', 'GLW', 'CTRA', 'DHI', 'DVN', 'DXC', 'EOG', 'EQT', 'FFIV', 'FITB', 'F', 'FCX', 'GE', 'HAL', 'HIG', 'HES', 'HPQ', 'HBAN', 'ILMN', 'INCY', 'ISRG', 'IVZ', 'J', 'KEY', 'KLAC', 'LRCX', 'LEN', 'MRO', 'MAS', 'MTCH', 'MET', 'MGM', 'MU', 'MHK', 'MOH', 'MNST', 'MOS', 'NTAP', 'NFLX', 'NRG', 'NVDA', 'OXY', 'ON', 'PXD', 'PRU', 'PTC', 'PHM', 'PWR', 'REGN', 'RF', 'RCL', 'CRM', 'SLB', 'STX', 'SWKS', 'STLD', 'TTWO', 'TPR', 'TER', 'TRMB', 'URI', 'VLO', 'VRTX', 'VTRS', 'WDC', 'WHR', 'WMB', 'WYNN', 'ZBRA', 'ZION']
	all_ema25s = []
	all_ema100s = []
	should_be_bought = []
	should_be_null = []
	open_positions = api.list_positions()
	already_bought = {}

	strengths = {}
	thresh = 0.2
	for ticker in potential_stocks:
		this_ema25, this_ema100 = get_emas(ticker)
		all_ema25s.append(this_ema25)
		all_ema100s.append(this_ema100)
		if (this_ema25[-1] - this_ema100[-1])/this_ema100[-1] > thresh:
			should_be_bought.append(ticker)
		elif this_ema25[-1] - this_ema100[-1] < 0:
			should_be_null.append(ticker)
	print(should_be_bought)
	print(should_be_null)

	for position in open_positions:
		print(f"Symbol: {position.symbol}, Qty: {position.qty}, Side: {position.side}, Avg Entry Price: {position.avg_entry_price}")
		if position.symbol in should_be_null:
			PlaceOrder(position.symbol, position.qty, "sell")
		else:
			already_bought[position.symbol] = position.qty

	rebalance(should_be_bought, already_bought)


def get_emas(symbol, timeframe = '1D'):

	end_date = str(datetime.datetime.now())
	end_date = end_date.split(" ")[0]+"T"+end_date.split(" ")[1]
	end_date = end_date.split(".")[0]+"Z"
	year = int(end_date.split("-")[0])
	year_start = year - 1
	start_date = str(year_start)+end_date.split(str(year))[1]

	limit = 500  # Number of data points to retrieve

	# Fetch historical data for the specified asset
	historical_data = api.get_bars(
		symbol,
		timeframe,
		start = start_date,
		end=end_date,
		limit=limit,
		adjustment='split'  # Use 'raw' for unadjusted data or 'split' for adjusted data
	)


	ema25 = [0]
	ema100 = [0]
	for i in historical_data:
		close_price = i.c
		ema25_day = close_price*(2/(1+25))+ema25[-1]*(1-(2/(1+25)))
		ema25.append(ema25_day)
		ema100_day = close_price*(2/(1+100))+ema100[-1]*(1-(2/(1+100)))
		ema100.append(ema100_day)

	return ema25, ema100

BuyAndSell()
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

key = 'PK86I7KGBNXWJV1Q52PG'
secret_key = '8Hl29lPbpKy5YYJrIUkenNP1j6iua559Kha0K6kw'
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

def PlaceOrder(ticker, qty):
	market_order_data = MarketOrderRequest(
					symbol=ticker,
					qty=qty,
					side=OrderSide.BUY,
					time_in_force=TimeInForce.GTC
					)

	market_order = trading_client.submit_order(order_data=market_order_data)

def LiquidAtClose(ticker, qty):
	market_order_data = MarketOrderRequest(
					symbol=ticker,
					qty=qty,
					side=OrderSide.SELL,
					time_in_force=TimeInForce.CLS
					)

	market_order = trading_client.submit_order(order_data=market_order_data)

def FindQuantity(budget, ticker, days_back = 1):
	#print("looped")
	present = datetime.datetime.now()
	present = datetime.datetime.timestamp(present)
	present = present - sec_in_day*days_back
	present = str(datetime.datetime.utcfromtimestamp(present).strftime('%Y-%m-%d'))
	#ticker_data = api.get_bars(ticker, TimeFrame.Day, "2023-7-23", "2023-7-24", adjustment='raw')
	return 100
	if ticker_data == []:
		return FindQuantity(budget, ticker, days_back+1)

	return budget/ticker_data[0].c

def MakePosition(budget_for_day, stock_list, sell_delay = 0):
	print(stock_list)
	#sell_delay ensures weekends are not counted in the holding period
	to_liquidate = {}
	date_to_sell = datetime.datetime.now()
	date_to_sell = datetime.datetime.timestamp(date_to_sell)
	date_to_sell = date_to_sell + sec_in_day*3 + sec_in_day*sell_delay
	for ticker in stock_list:
		print(ticker)
		quant = int(FindQuantity(budget_for_day/len(stock_list), ticker)) + 1  #want to make this work with fractional but int is bleh
		print(ticker, quant) 
		PlaceOrder(ticker, quant)
		#print(ticker, quant)
		try:
			to_liquidate[date_to_sell].append([ticker, quant])
		except:
			to_liquidate[date_to_sell] = []
			to_liquidate[date_to_sell].append([ticker, quant])

	return to_liquidate


sell_dicts = []

def BuyAndSell():
	all_money = account.buying_power
	budget_for_day = (float(all_money)/6)
	print(budget_for_day)
	day_of_week = datetime.datetime.now().weekday()
	weekend_adjust = 0
	if day_of_week > 1: #thats wednesday and onward
		weekend_adjust = 2 #add two days to the sell date so the weekend doesn't count toward holding time

	if day_of_week < 5:
		LastThreeDays = InsiderScraping.GetInsiderData()
		latest_day = LastThreeDays[0][0]
		stock_list = []
		for stuff in LastThreeDays:
			if stuff[0] == latest_day:
				stock_list.append(stuff[1])
		print(stock_list)
		sell_dicts.append(MakePosition(budget_for_day, stock_list, weekend_adjust))
		print(sell_dicts)
		time.sleep(60) #wait an hour to put in sell orders
		for i in sell_dicts:
			for dates in i.keys():
				if datetime.datetime.timestamp(datetime.datetime.now()) > dates:
					for pos in i[dates]: 
						LiquidAtClose(pos[0], pos[1])
					del i[dates]
	else: #no weekend trading
		pass

BuyAndSell()

	
	#time.sleep(60*60*23) #stupid ass way to do it but hey, itll work
	#need much better method of timing out events

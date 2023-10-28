from __future__ import (absolute_import, division, print_function,
						unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import matplotlib.pyplot as plt

import numpy as np


# Create a Stratey

class TestStrategy(bt.Strategy):
	params = (
		('maperiod1', 7),
		('maperiod2', 25),
		('maperiod3', 100),
	)

	def log(self, txt, dt=None):
		''' Logging function fot this strategy'''
		dt = dt or self.datas[0].datetime.date(0)
		print('%s, %s' % (dt.isoformat(), txt))

	def __init__(self, num_days = 0, num_in_market = 0):
		# Keep a reference to the "close" line in the data[0] dataseries
		self.dataclose = self.datas[0].close
		self.num_days = num_days
		self.num_in_market = num_in_market
		
		# To keep track of pending orders
		self.order = None


		self.ema7 = [bt.indicators.ExponentialMovingAverage(self.datas[0], period=self.params.maperiod1)]
		self.ema25 = [bt.indicators.ExponentialMovingAverage(self.datas[0], period=self.params.maperiod2)]
		self.ema100 = [bt.indicators.ExponentialMovingAverage(self.datas[0], period=self.params.maperiod3)]
		for t in range(1, len(self.datas)):
			self.ema7.append(bt.indicators.ExponentialMovingAverage(self.datas[t], period=self.params.maperiod1))
			self.ema25.append(bt.indicators.ExponentialMovingAverage(self.datas[t], period=self.params.maperiod2))
			self.ema100.append(bt.indicators.ExponentialMovingAverage(self.datas[t], period=self.params.maperiod3))

	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
			# Buy/Sell order submitted/accepted to/by broker - Nothing to do
			return

		# Check if an order has been completed
		# Attention: broker could reject order if not enough cash
		if order.status in [order.Completed]:
			if order.isbuy():
				pass
				#self.log('BUY EXECUTED, %.2f' % order.executed.price)
			elif order.issell():
				pass
				#self.log('SELL EXECUTED, %.2f' % order.executed.price)

			self.bar_executed = len(self)

		elif order.status in [order.Canceled, order.Margin, order.Rejected]:
			self.log('Order Canceled/Margin/Rejected')

		# Write down: no pending order
		self.order = None

	def next(self):
		self.num_days += 1

		# Simply log the closing price of the series from the reference
		#self.log('Close, %.2f' % self.dataclose[0])


		# Check if an order is pending ... if yes, we cannot send a 2nd one
		to_buy = []
		to_sell = []
		thresh = 0.2
		strengths = np.zeros(len(self.datas))
		for t in range(0, len(self.datas)):

			bleh = self.getposition(self.datas[t]).size
			if bleh > 0:
				strengths[t] = thresh/3

			if self.order:
				return

			# Not yet ... we MIGHT BUY if ...
			perc_ema = (self.ema25[t][-1] - self.ema100[t][-1])/self.ema100[t][-1]
			if perc_ema > thresh:

				#self.log('BUY CREATE, %.2f' % self.dataclose[0])

				# Keep track of the created order to avoid a 2nd order
				#shares = int((cerebro.broker.getvalue()/(1.2*self.datas[0].close)))
				to_buy.append(t)
				strengths[t] = perc_ema
				#self.order = self.buy(self.datas[0], size = shares)

			if self.getposition(self.datas[t]):
				self.num_in_market += 1
				# Already in the market ... we might sell
				if self.ema25[t][-1] < self.ema100[t][-1] or (self.datas[t].close - self.datas[t].open)/(self.datas[t].open) < -0.1:
					# SELL, SELL, SELL!!! (with all possible default parameters)
					#self.log('SELL CREATE, %.2f' % self.dataclose[0])

					# Keep track of the created order to avoid a 2nd order
					to_sell.append(t)
					strengths[t] = 0


		cash_money_honey = cerebro.broker.getvalue()

		print(cash_money_honey)
		denom = np.sum(strengths)
		if denom > 0:
			strengths/=denom
		for t in range(0, len(self.datas)):
			current_size = self.getposition(self.datas[t]).size
			shares = int((cash_money_honey*strengths[t]/(1.2*self.datas[t].close)))
			if current_size > shares:
				self.order = self.sell(self.datas[t], size = (current_size - shares))
			else:
				self.order = self.buy(self.datas[t], size = (shares - current_size))
		'''
		for t in to_sell:
			current_size = self.getposition(self.datas[t]).size
			self.order = self.close(self.datas[t])
		for t in range(0, len(self.datas)):
			bleh = self.getposition(self.datas[t]).size
			if t not in to_buy and bleh > 0:
				to_buy.append(t)
		for t in to_buy:
			current_size = self.getposition(self.datas[t]).size
			shares = int((cash_money_honey/(1.1*self.datas[t].close*len(to_buy))))
			if current_size > shares:
				self.order = self.sell(self.datas[t], size = (current_size - shares))
			else:
				self.order = self.buy(self.datas[t], size = (shares - current_size))
		'''


avgFinalVal = 0
if __name__ == '__main__':
	
	# Datas are in a subfolder of the samples. Need to find where the script is
	# because it could have been called from anywhere
	potential_stocks = ['AKAM', 'ALK', 'ALB', 'ALGN', 'AMZN', 'AMD', 'AIG', 'APA', 'ADSK', 'AXON', 'BKR', 'BAC', 'BBWI', 'BBY', 'BKNG', 'BWA', 'COF', 'KMX', 'CCL', 'CBRE', 'CNC', 'CRL', 'C', 'CMA', 'GLW', 'CTRA', 'DHI', 'DVN', 'DXC', 'EOG', 'EQT', 'FFIV', 'FITB', 'F', 'FCX', 'GE', 'HAL', 'HIG', 'HES', 'HPQ', 'HBAN', 'ILMN', 'INCY', 'ISRG', 'IVZ', 'J', 'KEY', 'KLAC', 'LRCX', 'LEN', 'MRO', 'MAS', 'MTCH', 'MET', 'MGM', 'MU', 'MHK', 'MOH', 'MNST', 'MOS', 'NTAP', 'NFLX', 'NRG', 'NVDA', 'OXY', 'ON', 'PXD', 'PRU', 'PTC', 'PHM', 'PWR', 'REGN', 'RF', 'RCL', 'CRM', 'SLB', 'STX', 'SWKS', 'STLD', 'TTWO', 'TPR', 'TER', 'TRMB', 'URI', 'VLO', 'VRTX', 'VTRS', 'WDC', 'WHR', 'WMB', 'WYNN', 'ZBRA', 'ZION']
	#potential_stocks = ['ALGN', 'AMZN', 'ADSK', 'AXON', 'BKR', 'BAC', 'COF', 'CCL', 'CBRE', 'CNC', 'C', 'CMA', 'CTRA', 'DHI', 'DVN', 'DXC', 'EOG', 'EQT', 'FFIV', 'FITB', 'F', 'FCX', 'GE', 'HBAN', 'ILMN', 'INCY', 'ISRG', 'IVZ', 'J', 'MRO', 'MTCH', 'MET', 'MGM', 'MU', 'MHK', 'MNST', 'MOS', 'NTAP', 'NFLX', 'NVDA', 'PRU', 'PTC', 'PHM', 'PWR', 'REGN', 'RF', 'SLB', 'STX', 'SWKS', 'STLD', 'TTWO', 'TPR', 'URI', 'VRTX', 'ZION']
	#the above list is pruned using only profitable stocks from 2003-2013

		# Create a cerebro entity
	cerebro = bt.Cerebro()

		# Add a strategy
	cerebro.addstrategy(TestStrategy)
		
	cerebro.addanalyzer(bt.analyzers.DrawDown, _name='mydraw')
	cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')

		# Create a Data Feed
	for ticker in potential_stocks:
		datapath = "C:\\Users\\Richard\\Documents\\Personal projects\\Restarting the AlgoBot\\Stocks_For_Black_Swan_Strat\\"+str(ticker)+".csv"
		data = bt.feeds.YahooFinanceCSVData(
			dataname=datapath,
			# Do not pass values before this date
			fromdate=datetime.datetime(2013, 1, 1),
			# Do not pass values before this date
			todate=datetime.datetime(2023, 12, 31),
			# Do not pass values after this date
			reverse=False)

		# Add the Data Feed to Cerebro
		cerebro.adddata(data)

		# Set our desired cash start
	cerebro.broker.setcash(10000.0)

	# Print out the starting conditions
	#print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

	# Run over everything
	result = cerebro.run()[0]
	# Print out the final result
	print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue(), "draw down:", result.analyzers.mydraw.get_analysis()['drawdown'], "draw down length:", result.analyzers.mydraw.get_analysis()['len'], "sharpe:", result.analyzers.mysharpe.get_analysis()['sharperatio'])
		



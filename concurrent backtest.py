from __future__ import (absolute_import, division, print_function,
						unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import matplotlib.pyplot as plt


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

		self.ema7 = bt.indicators.ExponentialMovingAverage(self.datas[0], period=self.params.maperiod1)
		self.ema25 = bt.indicators.ExponentialMovingAverage(self.datas[0], period=self.params.maperiod2)
		self.ema100 = bt.indicators.ExponentialMovingAverage(self.datas[0], period=self.params.maperiod3)

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
		if self.order:
			return

		# Check if we are in the market
		if not self.position:

			# Not yet ... we MIGHT BUY if ...
			if (self.ema25[-1] - self.ema100[-1])/self.ema100[-1] > 0.1:

				#self.log('BUY CREATE, %.2f' % self.dataclose[0])

				# Keep track of the created order to avoid a 2nd order
				shares = int((cerebro.broker.getvalue()/(1.2*self.datas[0])))
				self.order = self.buy(size = shares)

		else:
			self.num_in_market += 1
			# Already in the market ... we might sell
			if self.ema25[-1] < self.ema100[-1]:# or (self.datas[0].close - self.datas[0].open)/(self.datas[0].open) < 0.01:
				# SELL, SELL, SELL!!! (with all possible default parameters)
				#self.log('SELL CREATE, %.2f' % self.dataclose[0])

				# Keep track of the created order to avoid a 2nd order
				self.order = self.close()


avgFinalVal = 0
if __name__ == '__main__':
	
	# Datas are in a subfolder of the samples. Need to find where the script is
	# because it could have been called from anywhere
	potential_stocks = ['AKAM', 'ALK', 'ALB', 'ALGN', 'AMZN', 'AMD', 'AIG', 'APA', 'ADSK', 'AXON', 'BKR', 'BAC', 'BBWI', 'BBY', 'BKNG', 'BWA', 'COF', 'KMX', 'CCL', 'CBRE', 'CNC', 'CRL', 'C', 'CMA', 'GLW', 'CTRA', 'DHI', 'DVN', 'DXC', 'EOG', 'EQT', 'FFIV', 'FITB', 'F', 'FCX', 'GE', 'HAL', 'HIG', 'HES', 'HPQ', 'HBAN', 'ILMN', 'INCY', 'ISRG', 'IVZ', 'J', 'KEY', 'KLAC', 'LRCX', 'LEN', 'MRO', 'MAS', 'MTCH', 'MET', 'MGM', 'MU', 'MHK', 'MOH', 'MNST', 'MOS', 'NTAP', 'NFLX', 'NRG', 'NVDA', 'OXY', 'ON', 'PXD', 'PRU', 'PTC', 'PHM', 'PWR', 'REGN', 'RF', 'RCL', 'CRM', 'SLB', 'STX', 'SWKS', 'STLD', 'TTWO', 'TPR', 'TER', 'TRMB', 'URI', 'VLO', 'VRTX', 'VTRS', 'WDC', 'WHR', 'WMB', 'WYNN', 'ZBRA', 'ZION']

	for ticker in potential_stocks:
		# Create a cerebro entity
		cerebro = bt.Cerebro()

		# Add a strategy
		cerebro.addstrategy(TestStrategy)
		datapath = "C:\\Users\\Richard\\Documents\\Personal projects\\Restarting the AlgoBot\\Stocks_For_Black_Swan_Strat\\"+str(ticker)+".csv"
		cerebro.addanalyzer(bt.analyzers.DrawDown, _name='mydraw')
		cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')

		# Create a Data Feed
		data = bt.feeds.YahooFinanceCSVData(
			dataname=datapath,
			# Do not pass values before this date
			fromdate=datetime.datetime(2003, 1, 1),
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
		print(ticker, 'Final Portfolio Value: %.2f' % cerebro.broker.getvalue(), "draw down:", result.analyzers.mydraw.get_analysis()['drawdown'], "draw down length:", result.analyzers.mydraw.get_analysis()['len'], "sharpe:", result.analyzers.mysharpe.get_analysis()['sharperatio'])
		avgFinalVal += cerebro.broker.getvalue()/len(potential_stocks)
		#print(result.analyzers.mydraw.get_analysis())
		#for each in result[0].analyzers:
		#	each.print()
		#print('Sharpe Ratio:', result.analyzers.mydraw.get_analysis()['drawdown'])
		



print(avgFinalVal)
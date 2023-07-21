import requests
import csv
import pandas
import numpy as np
import matplotlib.pyplot as plt
import webbrowser
import time
import datetime
from bs4 import BeautifulSoup
#would be nice to investigate FinViz but it might have a block to webscraping, unsure bc im a noob


presentDate = datetime.datetime.now()
unix_timestamp = datetime.datetime.timestamp(presentDate)*1000
num_milsec_in_year = 365*24*60*60*1000


YahooFinance = "https://finance.yahoo.com/quote/AIM/history?p=AIM"
OpenInsider = 'http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=730&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&isofficer=1&iscob=1&isceo=1&ispres=1&iscoo=1&iscfo=1&isgc=1&isvp=1&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=100&page=1'
FinViz = "https://finviz.com/insidertrading.ashx?tc=1"

response = requests.get(OpenInsider)
soup = BeautifulSoup(response.text, 'html.parser')

body = soup.find("body")
div = soup.find("div")
table = soup.find("table")
table_body = soup.find("body")
all_rows = soup.find_all("tr")
stocks_and_dates = []
for row in all_rows:
	td = row.find_all("td")
	#want index 2 and 3 which correspond to the trade date and the ticker respectively
	try:
		date = str(td[2].find("div"))
		date = date.split(">")[1]
		date = date.split("<")[0]
		ticker = str(td[3].find("b").find("a")["href"])
		ticker = ticker.split("/")[1]
		ticker = ticker.split(".")[0]
		stocks_and_dates.append([date, ticker])
		#print(date, ticker)
	except:
		pass

print(stocks_and_dates)
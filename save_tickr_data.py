import pandas
import webbrowser
import time
import datetime
import os

def DownAndLoadData(ticker, wod = "wk"):
	#ticker is stock name ticker of course
	#wod is week or day, default to weekly data, pass "d" for daily
	#ensures most recent data is used
	expected_path = "C:\\Users\\Richard\\Downloads\\"+str(ticker)+".csv"
	try:
		os.remove(expected_path)
	except:
		pass
	presentDate = datetime.datetime.now()
	unix_timestamp = datetime.datetime.timestamp(presentDate)*1000
	num_milsec_in_year = 365*24*60*60*1000
	#print(unix_timestamp-num_milsec_in_year)

	#automate download of yahoo stock data
	download_link = "https://query1.finance.yahoo.com/v7/finance/download/"+str(ticker)+"?period1="+str(int(unix_timestamp-num_milsec_in_year)//1000)+"&period2="+str(int(unix_timestamp)//1000)+"&interval=1"+wod+"&events=history&includeAdjustedClose=true"
	webbrowser.open(download_link)
	time.sleep(5) #can't try to open the file before it finished downloading
	data = pandas.read_csv("C:\\Users\\Richard\\Downloads\\"+str(ticker)+".csv")
	return data

#print(DownAndLoadData("TSLA"))

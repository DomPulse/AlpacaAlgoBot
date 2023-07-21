from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
import save_tickr_data as std
import string
import random
import numpy as np
import joblib

def GiveTrainData(time_data):
	all_target_data = []
	all_input_data = []
	for i in range(7, len(time_data)-1):
		target_dataframe = time_data.loc[[i+1]]
		target_data = (np.max(target_dataframe["Close"]) > np.max(target_dataframe["Open"]))*1
		all_target_data.append(target_data)
		input_data = []
		for j in range(0, 7):
			today_data = time_data.loc[[i-j]]
			yest_data = time_data.loc[[i-1-j]]
			OldOpen = np.max(today_data["Open"])
			OldClose = np.max(today_data["Close"])
			OldHigh = today_data["High"]
			OldLow = today_data["Low"]
			NewClose = 0.25*(OldOpen + OldClose + OldHigh + OldLow)
			NewOpen = 0.5*(yest_data["Open"] + yest_data["Close"])
			NewHigh = np.max([OldHigh, NewClose, NewOpen])
			NewLow = np.min([OldLow, NewClose, NewOpen])
			NewClose = np.max([NewClose])
			NewOpen = np.max([NewOpen])
			input_data.append([NewClose-NewOpen, NewHigh-NewOpen, NewLow-NewOpen])
		input_data = np.concatenate(input_data)
		all_input_data.append(input_data)
	#print(all_input_data)
	#print(all_target_data)
	return all_input_data, all_target_data


epoch = 0
model = AdaBoostClassifier(n_estimators=50, learning_rate=1)


this_ticker = std.DownAndLoadData("AMZN")
X_train, y_train = GiveTrainData(this_ticker)
model = model.fit(X_train, y_train)


while epoch < 100:
	print(epoch)
	ticker = ""
	for j in range(0, 3):
		randomLetter = chr(random.randint(ord('A'), ord('Z')))
		ticker += randomLetter
	try:
		this_ticker = std.DownAndLoadData(ticker)
		X_train, y_train = GiveTrainData(this_ticker)
		model = model.fit(X_train, y_train)
		epoch += 1
	except:
		pass
		

joblib.dump(model, f'adaboost_model_stock.pkl')

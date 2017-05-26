from similarity_metrics import csv_to_dict
from sklearn.ensemble import RandomForestRegressor	
from sklearn.metrics import explained_variance_score, r2_score
import pandas as pd
import numpy as np
from itertools import groupby
from operator import itemgetter

pd.set_option('display.expand_frame_repr', False)
MSEs = pd.read_csv("mse_bricks_001_100window_random.csv", names = ["V1", "V2","Lum1", "Con1", "Hue1", "Sat1","Lum2", "Con2", "Hue2", "Sat2", "MSE"], header = None)
VARIANT_DICT = csv_to_dict("variant_list.csv")


def split_dataset(data, proportion):
	data['training'] = np.random.uniform(0, 1, len(data)) <= proportion
	train, test = data[data['training']==True], data[data['training']==False]
	return train, test

def test_extremes(r):
	seen = list(zip(MSEs["V1"], MSEs["V2"]))
	pairs_dict = {}
	dict_idx = 0
	for i in xrange(1,r+1):
		for j in xrange(9317-r,9318):
			pairs_dict[dict_idx]=[i,j,
									  VARIANT_DICT[str(i)][0],
									  VARIANT_DICT[str(i)][1],
									  VARIANT_DICT[str(i)][2],
									  VARIANT_DICT[str(i)][3],
									  VARIANT_DICT[str(j)][0],
									  VARIANT_DICT[str(j)][1],
									  VARIANT_DICT[str(j)][2],
									  VARIANT_DICT[str(j)][3]]
			dict_idx+=1
	pairs = pd.DataFrame.from_dict(pairs_dict, orient="index")
	pairs.columns = ["V1", "V2","Lum1", "Con1", "Hue1", "Sat1","Lum2", "Con2", "Hue2", "Sat2"]
	return pairs

def create_remaining_pairs():
	#pairs = pd.DataFrame(columns = ["V1", "V2","Lum1", "Con1", "Hue1", "Sat1","Lum2", "Con2", "Hue2", "Sat2"])
	seen = list(zip(MSEs["V1"], MSEs["V2"]))

	pairs_dict = {}
	dict_idx = 0
	print type(MSEs.iloc[0]["V1"])
	for i in xrange(1,10):
		for j in xrange(i+1, 11):
			if (i,j) not in seen or (j,i) not in seen:
				pairs_dict[dict_idx]=[i,j,
									  VARIANT_DICT[str(i)][0],
									  VARIANT_DICT[str(i)][1],
									  VARIANT_DICT[str(i)][2],
									  VARIANT_DICT[str(i)][3],
									  VARIANT_DICT[str(j)][0],
									  VARIANT_DICT[str(j)][1],
									  VARIANT_DICT[str(j)][2],
									  VARIANT_DICT[str(j)][3]]
				dict_idx+=1
				print dict_idx

	pairs = pd.DataFrame.from_dict(pairs_dict, orient="index")
	pairs.columns = ["V1", "V2","Lum1", "Con1", "Hue1", "Sat1","Lum2", "Con2", "Hue2", "Sat2"]
	return pairs

def col_diff(dataframe):
	df = dataframe.copy()
	df["Lum1"] = df["Lum1"].sub(df["Lum2"],axis=0)
	df["Con1"] = df["Con1"].sub(df["Con2"],axis=0)
	df["Hue1"] = df["Hue1"].sub(df["Hue2"],axis=0)
	df["Sat1"] = df["Sat1"].sub(df["Sat2"],axis=0)
	for i in ["Lum2","Con2","Hue2","Sat2"]:
		df = df.drop(i,1)
	df.columns = ["V1", "V2","LumD", "ConD", "HueD", "SatD", "MSE"]
	return df

def main():
	global MSEs


	MSE_diff = col_diff(MSEs)

	train, test = split_dataset(MSE_diff, 0.9)

	print len(MSE_diff)
	print "Train:",len(train)
	print "Test:",len(test)
	print train.head()
	print test.head()

	features = MSEs.columns[2:10]

	#test_pairs = test_extremes(100)
	#print test_pairs.head()

	clf = RandomForestRegressor(n_jobs=-1)
	# clf.fit(MSEs[features], MSEs["MSE"])
	test_data = pd.read_csv("mse_bricks_001_first_last.csv", names = ["V1", "V2","Lum1", "Con1", "Hue1", "Sat1","Lum2", "Con2", "Hue2", "Sat2", "MSE"], header = None)
	clf.fit(train[features], train["MSE"])
	preds = clf.predict(test[features])
	#print preds
	print "FEATURE IMPORTANCES:",list(zip(train[features], clf.feature_importances_))

	print "EXPLAINED VARIANCE SCORE:",explained_variance_score(test["MSE"],preds)

	print "R2 SCORE:",r2_score(test["MSE"],preds)

	print "###############"
	print "RUN 1"
	
	preds1 = clf.predict(test_data[features])
	print "FEATURE IMPORTANCES:",list(zip(MSEs[features], clf.feature_importances_))

	test_data["Predicted MSE"] = preds1
	print test_data.head()
	print "EXPLAINED VARIANCE SCORE:",explained_variance_score(test_data["MSE"],preds1)

	print "R2 SCORE:",r2_score(test_data["MSE"],preds1)

	# print "###############"
	# print "RUN 2"
	
	# preds2 = clf.predict(test_data[features])
	# print "FEATURE IMPORTANCES:",list(zip(MSEs[features], clf.feature_importances_))

	# test_data["Predicted MSE"] = preds1
	# print test_data.head()
	# print "EXPLAINED VARIANCE SCORE:",explained_variance_score(test_data["MSE"],preds2)

	# print "R2 SCORE:",r2_score(test_data["MSE"],preds2)

	# print "###############"
	# print "RUN 3"
	
	# preds3 = clf.predict(test_data[features])
	# print "FEATURE IMPORTANCES:",list(zip(MSEs[features], clf.feature_importances_))

	# test_data["Predicted MSE"] = preds1
	# print test_data.head()
	# print "EXPLAINED VARIANCE SCORE:",explained_variance_score(test_data["MSE"],preds3)

	# print "R2 SCORE:",r2_score(test_data["MSE"],preds3)



if __name__ == '__main__':
	main()
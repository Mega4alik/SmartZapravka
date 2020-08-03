#python3 app.py
import string
import os 
import subprocess
import json
import io
import pymysql
import numpy
import math

import flask
from flask import Flask
from flask import make_response
from flask import request
from flask import jsonify

from sklearn.externals import joblib
from sklearn.metrics import accuracy_score, mean_squared_error, average_precision_score
from sklearn.utils import shuffle    
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
#from skmultilearn.problem_transform import BinaryRelevance
#from sklearn.naive_bayes import GaussianNB
from sklearn import svm
#from sklearn.linear_model import LogisticRegression
#from skmultilearn.problem_transform import BinaryRelevance


PRODUCT_CATEGORIES_N = 49
USER_CATEGORIES_N = 23

def connect():
  return pymysql.connect(host='localhost',user='root',password='',db='zapravka',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

def file_get_contents(filename):
  return open(filename).read()

def file_put_contents(file_path, st):
  #f1 = open(file_path, 'w')
  f1 = io.open(file_path, mode="w", encoding="utf-8")
  f1.write(st)
  f1.close()



#fuel
def refill_prepare():
	import pandas
	from datetime import datetime
	import dateparser
	df = pandas.read_csv('transaction_report.csv', infer_datetime_format=True)
	d = {}
	stations = []

	for index, row in df.iterrows():	
		#print(index)     
		#if (index > 200): break
		login = row[0]
		station = row[1]
		date = row[2]
		fuel_type = row[3]
		if math.isnan(login) or login=="77000000000" or login=="77000000000.0" or login==77000000000.0: continue
		if "2017" in date: continue #or "2018" in date

		new = False
		if not login in d:
			d[login] = []
			new = True

		if new==False:		
			a = dateparser.parse(date)
			b = dateparser.parse(d[login][0]['date'])
			diff = a - b
			date_diff = diff.days
		else:
			date_diff = 0

		if not station in stations: stations.append(station)

		d[login].append({'login':int(login), 'station':station, 'station_idx':stations.index(station), 'date':date, 'fuel_type':fuel_type, 'date_diff':date_diff})
		#print(d[login][-1])
	
	print(stations)


	Xd = []
	Xs = []
	Y_date_diff = []
	Y_station_idx = []
	for login in d:
		#print(d[login])		
		a = d[login]
		for i in range(0, len(a)-3, 2):
			#x = [ [a[i]['date_diff'], a[i]['station_idx']], [a[i+1]['date_diff'], a[i+1]['station_idx']], [a[i+2]['date_diff'], a[i+2]['station_idx']] ]
			dd0 = a[i+0]['date_diff'] - a[i]['date_diff']
			dd1 = a[i+1]['date_diff'] - a[i]['date_diff']
			dd2 = a[i+2]['date_diff'] - a[i]['date_diff']
			dd3 = a[i+3]['date_diff'] - a[i]['date_diff']
			s0 = a[i]['station_idx']
			s1 = a[i+1]['station_idx']
			s2 = a[i+2]['station_idx']
			s3 = a[i+3]['station_idx']
			xd = [dd0, s0, dd1, s1, dd2, s2]
			#xs = [ dd0, s0, dd1, s1, dd2, s2 ] #[s0, s1, s2] #
			xs = [0] * len(stations)
			xs[s0] += 1
			xs[s1] += 1
			xs[s2] += 1
			y_date_diff = dd3
			y_station_idx = s3
			Xd.append(xd)
			Xs.append(xs)
			Y_date_diff.append(y_date_diff)
			Y_station_idx.append(y_station_idx)

	file_put_contents("refill_Xd.json", json.dumps(Xd))
	file_put_contents("refill_Xs.json", json.dumps(Xs))
	file_put_contents("refill_Y_date_diff.json", json.dumps(Y_date_diff))
	file_put_contents("refill_Y_station_idx.json", json.dumps(Y_station_idx))        
	file_put_contents("stations.json", json.dumps(stations))



def refill_train():
	DIVIDER = 150
	with open('refill_Xd.json') as f: Xd = json.load(f)
	with open('refill_Xs.json') as f: Xs = json.load(f)
	with open('refill_Y_date_diff.json') as f: Yd = json.load(f)  
	with open('refill_Y_station_idx.json') as f: Ys = json.load(f)  	

	clf_d = RandomForestRegressor(n_estimators=100) 
	#clf_s = RandomForestClassifier(n_estimators=100) 
	clf_s = svm.LinearSVC()
	clf_d.fit(Xd[DIVIDER:],Yd[DIVIDER:])
	clf_s.fit(Xs[DIVIDER:],Ys[DIVIDER:])
	joblib.dump(clf_d, 'model_refill_d.save')    
	joblib.dump(clf_s, 'model_refill_s.save')    

	predictions_d = clf_d.predict(Xd[:DIVIDER])
	predictions_s = clf_s.predict(Xs[:DIVIDER])
	for i in range(len(predictions_s)):
		print(int(predictions_d[i]), Yd[i])
	
	print(mean_squared_error(Yd[:DIVIDER], predictions_d))
	print(accuracy_score(Ys[:DIVIDER], predictions_s))



def refill_predict(arr): #[{'date_diff':0, 'login':'', 'station':''}, {}]
	with open('stations.json') as f: stations = json.load(f)
	dd0 = arr[0]['date_diff']
	s0 = stations.index(arr[0]['station'])
	dd1 = arr[1]['date_diff']
	s1 = stations.index(arr[1]['station'])
	dd2 = arr[2]['date_diff']
	s2 = stations.index(arr[2]['station'])
	xd = [ dd0, s0, dd1, s1, dd2, s2 ]
	#xs = [ dd0, s0, dd1, s1, dd2, s2 ] #
	xs = [0] * len(stations)
	xs[s0] += 1
	xs[s1] += 1
	xs[s2] += 1

	clf_d = joblib.load('model_refill_d.save') 	
	clf_s = joblib.load('model_refill_s.save') 	
	pre_d = int(clf_d.predict([xd])[0])
	pre_s = clf_s.predict([xs])[0]
	return pre_d, stations[pre_s]
#endOf fuel



def import_checks(fileid):     
	import pandas
	df = pandas.read_csv('checks'+str(fileid)+'.csv')
	a = []
	for index, row in df.iterrows():
		try:
			print(index)        
			cid = row[0]
			pname = row[1]
			particle = int(row[6])
			cdate = row[5]    
			#print(cid, pname, particle, cdate)            
			try:
				cid = int(cid)            
				a.append({'cid':cid, 'cdate':cdate, 'products':[{'pname':pname,'particle':particle}]  })            
			except Exception as e:
				a[-1]['products'].append({'pname':pname,'particle':particle})            
		except Exception as ex:
			print(ex)
		#if (len(a)>10): break
	
	
	conn = connect()
	cursor = conn.cursor()
	for x in a:
		try:
			products = []
			for q in x['products']: products.append(q['particle'])
			products_key = str(sorted(products))
			cursor.execute('INSERT INTO checks(fileid, cid, cdate, products, products_key) VALUES(%s, %s, %s, %s, %s)',
				(fileid,  x['cid'],  x['cdate'], json.dumps(x['products'], ensure_ascii=False), products_key))
			conn.commit()
		except Exception as e:
			print(e)            
	conn.close()            
	


def get_products_map():
	conn = connect()        
	cursor = conn.cursor()        
	products_map = {}
	cursor.execute('SELECT * FROM products ORDER BY id')         
	products = cursor.fetchall()                
	for p in products:
		products_map[p["particle"]] = p["pcategory"]
	file_put_contents("products_map.json", json.dumps(products_map))
	return products_map


def prepare_dataset():
	conn = connect()        
	cursor = conn.cursor()  	
	X = []
	Y = []
	infos = []              
	products_map = get_products_map()   
	cursor.execute('SELECT * FROM checks WHERE user_categories IS NOT NULL ORDER BY id')
	checks = cursor.fetchall()
	for q in checks:
		user_categories = json.loads(q["user_categories"])
		pcategories = []
		products_key = json.loads(q["products_key"])
		for particle in products_key:
			pcategories.append(products_map[particle])
		y = [int(x) for x in user_categories]
		X.append(pcategories)
		Y.append(y)
		infos.append(user_categories)

	file_put_contents("X.json", json.dumps(X))
	file_put_contents("Y.json", json.dumps(Y))        
	file_put_contents("infos.json", json.dumps(infos))
			
		

def train():
	DIVIDER = 150
	with open('X.json') as f: Xin = json.load(f)
	with open('Y.json') as f: Yin = json.load(f)  
	with open('infos.json') as f: infos = json.load(f)  

	Xin, Yin, infos = shuffle(Xin, Yin, infos)

	input_len = PRODUCT_CATEGORIES_N +1 #max(Xin)[0] + 1
	classes_n = USER_CATEGORIES_N +1 #max(Yin)[0] + 1
	print(input_len, classes_n, len(Xin))	
	X = []
	Y = []
	for row in Xin:
		a = [0]*input_len
		for x in row: a[x] = 1
		X.append(a)
	
	for row in Yin:
		a = [0] * classes_n        
		for y in row: a[y] = 1
		Y.append(a)
	
	
	if 1==2:
		clf = {}
		print("Traininig..")
		for i in range(0, classes_n):
			Y2 = [row[i] for row in Y] #0/1
			clf[i] = RandomForestClassifier(n_estimators=100)
			clf[i].fit(X[DIVIDER:],Y2[DIVIDER:])            
		print("Done.")
		#DIVIDER = 10 #temp
		predictions = []
		for i in range(DIVIDER):
			x = X[i]            
			pre = [clf[j].predict([x])[0] for j in range(0, classes_n)] #vector
			print(pre)
			print("\n")
			predictions.append(pre) 

		testY = numpy.array(Y[:DIVIDER])
		predictions = numpy.array(predictions)
		#print(len(testY), len(predictions), len(testY[0]), len(predictions[0]))        
		#print(testY, "-----", predictions)                
		
		for i in range(len(predictions)):                        
			pre = predictions[i]
			ref = Y[i]
			for j in range(len(pre)):
				if pre[j]==1:  print(j)
			print(infos[i])            
			print("\n")
		print(accuracy_score(testY,  predictions))                


	else:
		X = numpy.array(X)
		Y = numpy.array(Y)
		clf = RandomForestClassifier(n_estimators=100)
		#clf = BinaryRelevance(GaussianNB())
		#clf = svm.LinearSVC()
		#clf = LogisticRegression(random_state=0)
		clf.fit(X[DIVIDER:],Y[DIVIDER:])
		joblib.dump(clf, 'model.save')    
		predictions = clf.predict(X[:DIVIDER])
		#print(Y[:DIVIDER], predictions)                            
		for i in range(len(predictions)):
			#print(predictions[i], '---', Y[i])            
			pre = predictions[i]
			ref = Y[i]
			for j in range(len(pre)):
				if pre[j]==1:  print(j)
			print(infos[i])            
			print("\n")
		print(accuracy_score(Y[:DIVIDER], predictions))



def predict(particles): #[2,4,5]
	#products_map = get_products_map() #particle -> pcategory
	with open('products_map.json') as f: products_map = json.load(f)	
	clf = joblib.load('model.save') 	
	input_len = PRODUCT_CATEGORIES_N + 1
	x = [0] * input_len
	for particle in particles: 
		if (str(particle) in products_map): x[products_map[str(particle)]] = 1
	pre = clf.predict([x])[0]
	user_categories = []
	for i in range(len(pre)):
		if pre[i]==1: user_categories.append(i)
	return user_categories




app = Flask(__name__)
#from app import routes

@app.route('/', methods=['GET'])
def home():
	action = request.args.get('action')

	if action=="uc_predict":
		particles = json.loads(request.args.get('particles'))
		print("uc_predict", particles)
		return jsonify(predict(particles))
		
	elif action=="refill_predict": 
		#http://zapravka.ailabs.kz:5000?action=refill_predict&arr=[{"station": "GasOilProm 4 BJ", "date_diff": 0, "login": 0}, {"station": "GasOilProm 4 BJ", "date_diff": 5, "login": 0}, {"station": "GasOilProm 4 BJ", "date_diff": 25, "login": 0}]
		arr = json.loads(request.args.get('arr'))
		return jsonify(refill_predict(arr))
	return "no action"

	
if __name__ == "__main__":
	app.run(host='0.0.0.0',port='5000')
	
	#recommendations system
	#import_checks(2)
	#prepare_dataset() #1
	#train() #2
	#print(predict([2025, 33101, 33103])) #8,9


	#refill
	#refill_prepare() #1
	#refill_train() #2
	#arr = [{'date_diff':0, 'station':'GasOilProm 4 BJ', 'login':0}, {'date_diff':5, 'station':'GasOilProm 4 BJ', 'login':0}, {'date_diff':25, 'station':'GasOilProm 4 BJ', 'login':0}]
	#print(refill_predict(arr))


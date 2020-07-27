# SmartZapravka
 

1) Installation
- Install python3 (tested on 3.5.2)
- Install pip3
- Install requirement as pip3 install -r requirement.txt
1.1) Start application as python3 app.py. The app will at localhost:5000


2) User Category Detection
2.1) Usage
action=uc_predict, 
particles = [<product article>]
 
Call Example - http://zapravka.ailabs.kz:5000/?action=uc_predict&particles=[11125]


3) Refill Date and Stations Prediction
3.1) Usage
http://zapravka.ailabs.kz:5000?action=refill_predict&arr=[{"station": "GasOilProm 4 BJ", "date_diff": 0, "login": 0}, {"station": "GasOilProm 4 BJ", "date_diff": 5, "login": 0}, {"station": "GasOilProm 4 BJ", "date_diff": 25, "login": 0}]

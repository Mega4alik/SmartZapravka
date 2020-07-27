# SmartZapravka
 

1) Installation
- Install python3 (tested on 3.5.2)
- Install pip3
- Install requirements as pip3 install -r requirements.txt.

1.1) Start application as python3 app.py. The app will at localhost:5000



2) User Category Detection (выявление категорий пользователя)

2.1) Usage.

Для вызова данной функции нужно передать action=uc_predict, и артиклы товаров текущего чека (particles = [<product article>]).
Рабочий пример вызова - http://zapravka.ailabs.kz:5000/?action=uc_predict&particles=[11125]
Ответом будем массив [<user_category_id>]. Таблицу категорий пользователей смотрите тут - https://drive.google.com/drive/folders/1kABvpya0xbKDUd2XHhg_s7NpHa5RkY0a?usp=sharing
 
 

3) Refill Date and Stations Prediction (предсказывание след даты и станции заправки)

3.1) Usage.

Для вызова данной функции нужно передать информацию о предыдущих 3 заправках. 
action=refill_predict,  arr=[
 {'station':<Название станции>, 'login':<логин>, 'date_diff':<всегда равна нулю>}, 
 {'date_diff':<разница дней между второй и первой заправки в данном списке>, 'station':<Название станции>, 'login':<логин>,},
 {'date_diff':<разница дней между третей и первой заправки в данном списке>, 'station':<Название станции>, 'login':<логин>,},
]. 

Ответом будет [разница дней между предсказываемой и первой заправкой передаваемой в данном списке, название станции]

Например, последние 3 заправки пользователя с логин "0" были 2-го, 7-го и 27-го июля 2020 года на станции "GasOilProm 4 BJ".  Тогда запрос будет таким: 
http://zapravka.ailabs.kz:5000?action=refill_predict&arr=[{"station": "GasOilProm 4 BJ", "date_diff": 0, "login": 0}, {"station": "GasOilProm 4 BJ", "date_diff": 5, "login": 0},  {"station": "GasOilProm 4 BJ", "date_diff": 25, "login": 0}]

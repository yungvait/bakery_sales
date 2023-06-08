import pandas as pd 
import numpy as np
import matplotlib.pyplot  as plt
import statsmodels as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error
import math

from pmdarima import auto_arima


data = pd.read_csv('Bakery_sales.csv', delimiter=';', encoding='Windows-1251', dtype={'unit_price': float, 'total_price': float}, decimal=',')


# Преобразование столбца 'date' в тип datetime
data['date'] = pd.to_datetime(data['date'], dayfirst=True)

#converting time to datetime
data['time'] = pd.to_datetime(data['time'], format="%H:%M")
# Установка столбца 'date' в качестве индекса
data.set_index('date', inplace=True)
#Удаление отрицательных значений
data = data[(data['unit_price'] > 0) & (data['Quantity'] > 0)]
#Создание таблицы еждневных продаж
daily_sales = data.groupby('date').agg({'total_price':'sum'}).reset_index()
#set date as index
daily_sales.set_index('date', inplace = True)
#train - test split
#creating a table of weekly sales
weekly_sales = daily_sales.resample('W').sum()
result = adfuller(weekly_sales)

# Печать результата теста
print('ADF Statistic:', result[0])
print('p-value:', result[1])
train = weekly_sales[:int(0.7*len(weekly_sales))]
test = weekly_sales[int(0.7*len(weekly_sales)):]

model_auto_arima = auto_arima(train, trace=True,start_p=0, start_q=0, start_P=0, start_Q=0,
                  max_p=5, max_q=5, max_P=3, max_Q=3, seasonal=True,maxiter=50,m = 52, D = 1,
                  information_criterion='aic',stepwise=False, suppress_warnings=True,
                  error_action='ignore',approximation = False)
model_auto_arima.fit(train)
import datetime
import pandas as pd
import numpy as np
import requests
from requests.auth import HTTPBasicAuth
from flask import Flask

datetime = datetime.datetime.now()
# Would always forecast over moving 30-minute intervals (i.e. 1:00-1:30, 1:05-1:35, etc.), would forecast this
# way every five minutes (when called)
def future_weather():
    url = 'https://api.solcast.com.au/utility_scale_sites/7fcf-9bc4-c408-47f2/weather/forecasts?period=PT5M&format=json'
    r = requests.get(url, auth=HTTPBasicAuth('TqQsNurmYZY8DK55Y5aGMhMbzFTucrDa',''))
    r = r.json()
    r = r['forecasts']
    data = []
    for i in range(len(r)):
        data.append([r[i]['air_temp'],r[i]['cloud_opacity']])
    return data

def all_weather():
    url = 'some url for current clouds and temperature'
    r = requests.get(url, auth=HTTPBasicAuth('TqQsNurmYZY8DK55Y5aGMhMbzFTucrDa',''))
    r = r.json()
    clouds = r['estimated_actuals'][0]['cloud_opacity']
    temperature = r['estimated_actuals'][0]['air_temp']
    past_weather = pd.read_csv('past_weather.csv',header=None)
    past_weather = past_weather.values.tolist()
    del(past_weather[0])
    past_weather.append([temperature,clouds])
    weather = past_weather+future_weather()
    data = pd.DataFrame(past_weather)
    np.savetxt('past_weather.csv', data, delimiter=",")
    return weather

def demands():
    url = 'some url for current demand'
    r = requests.get(url, auth=HTTPBasicAuth('TqQsNurmYZY8DK55Y5aGMhMbzFTucrDa',''))
    r = r.json()
    current_demand = r['Demand']
    past_demands = pd.read_csv('past_demands.csv',header=None)
    past_demands = past_demands.values.tolist()
    del(past_demands[0])
    past_demands.append([current_demands])
    data = pd.DataFrame(past_demands)
    np.savetxt('past_demands.csv', data, delimiter=",")
    return past_demands

def data_formatting():
    data = []
    weather = all_weather()
    demands = demands()
    temperature = []
    clouds = []
    demand = []

    for i in range(int(len(weather)/6)):
        t_temp = 0
        c_temp = 0
        for j in range(6):
            t_temp += weather[6*i+j][0]
            c_temp += weather[6*i+j][1]
        temperature.append(t_temp/6)
        clouds.append(c_temp/6)

    for i in range(int(len(demands)/6)):
        d_temp = 0
        for j in range(6):
            d_temp += weather[6*i+j][0]
        demand.append(d_temp/6)

        
    for i in range(96):
        add = []
        months = [31,28,31,30,31,30,31,31,30,31,30,31]
        time = datetime.hour*2+datetime.minute//30
        day = datetime.day-1 + sum(months[:datetime.month-1]) + (datetime.year-2021)*365
        
        add.append(temperature[16+i]) # current temperature
        add.append(np.mean(temperature[16+i-2:16+i])) # Past hour
        add.append(np.mean(temperature[16+i-8:16+i-2]))# mean 3 hours before that
        add.append(np.mean(temperature[16+i-16:16+i-8]))# mean 4 hours before that
        add.append(clouds[16+i]) # current cloud opacity
        
        x = np.cos((time+i)%48*np.pi/24) # Take time period (48 total)
        y = np.sin((time+i)%48*np.pi/24) # Time is cyclical, hence, take cos, sin
        add.append(x) 
        add.append(y)

        x = np.cos((day%365)*np.pi/182.5)
        y = np.cos((day%365)*np.pi/182.5)
        add.append(x) 
        add.append(y)
        
        d = day%7 # Day of Week, categorical (dummy variables) - First day is a Friday
        for i in range(7):
            if i == d:
                add.append(1)
            else:
                add.append(0)
                
        for i in range(1,49):
            add.append(demand[-i])
            
    data = pd.DataFrame(data)    
    return data



def optimiser(): # Outputs the predicted load over the next 48 hours
    
    forecast = []
    data = data_formatting()
    data = data.values.tolist()
    
    for period in range(len(data)):

        name = 'Marciano' + str(period) + '.pickle'
        
        optimiser =  pickle.load(open(name, "rb")) # Returns a previously trained model for given time period
        prediction = float(optimiser.predict(data[i]))
        forecast.append(prediction) # Forecasts the demands

    return forecast


# Section 3: Sending forecasted data
app = Flask(__name__)

@app.route('/',methods = ['GET'])
def forecasting():
   if requests.method == 'GET':
        data = optimiser()
        x = {'Demands': data}
        return json.dumps(x)


if __name__ == '__main__':
   app.run(debug = True)




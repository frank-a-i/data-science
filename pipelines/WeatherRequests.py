import os
import pickle
import requests
import datetime
import pandas as pd
from numpy import mean
from common import Config
from datetime import datetime
from dataclasses import dataclass


class SequenceFeature:
    def __init__(self, samples):
        self.min = min(samples)
        self.max = max(samples)
        self.mean = mean(samples)
    def __repr__(self):
        return f"{self.min} >= {self.mean} >= {self.max}"

@dataclass
class WeatherFeatures:
    temp: SequenceFeature
    relHumidity: SequenceFeature
    rain: SequenceFeature
    weatherCode: SequenceFeature
    cloudCover: SequenceFeature
    windSpeed: SequenceFeature
    soilMoisture: SequenceFeature
    daylightDuration: float
    sunshineDuration: float
    
@dataclass
class Datespan:
    begin: datetime
    end: datetime

class WeatherRequests:
    def __init__(self):
        self._features = "hourly="
        self._features += "temperature_2m"
        self._features += ",relative_humidity_2m"
        self._features += ",rain"
        self._features += ",weather_code"
        self._features += ",cloud_cover"
        self._features += ",wind_speed_10m"
        self._features += ",soil_moisture_0_to_7cm"
        self._features += "&daily="
        self._features += "daylight_duration"
        self._features += ",sunshine_duration"

        self._maxHourlyRequests = 5000
        self._maxDailyRequests = 10000
        self._urlWeatherApi = "https://archive-api.open-meteo.com/v1/archive"

    def _requestData(self, longitude: float, lattitude: float, queryDate: datetime) -> (int, dict):
        apiDate = f"{queryDate.year}-{queryDate.month:02d}-{queryDate.day:02d}"
        
        timeRange = f"start_date={apiDate}&end_date={apiDate}"
        apiCmd = f"{self._urlWeatherApi}?latitude={lattitude}&longitude={longitude}&{self._features}&{timeRange}"
        receivedData = requests.get(apiCmd).json()

        foundMatch = False
        timefocusId = None
        try:
            for idt, curTime in enumerate(receivedData["hourly"]["time"]):
                curResponseDateTime = datetime.strptime(curTime, "%Y-%m-%dT%H:%M")
                if (curResponseDateTime.year == queryDate.year and 
                    curResponseDateTime.month == queryDate.month and  
                    curResponseDateTime.day == queryDate.day and 
                    curResponseDateTime.hour == queryDate.hour):
                    foundMatch = True
                    timefocusId = idt
                    break
        except Exception as e:
            print(f"Unexpected requests response for cmd\n{apiCmd}\nresponse\n{receivedData}\nException\n{e}")
        
        
        assert timefocusId != None, "Unexpected: Could not find API date"
            
        return (timefocusId, receivedData)

    def getStatisticsFor(self,
        longitude: float,
        lattitude: float,
        date: datetime):

        timefocusId, receivedData = self._requestData(longitude, lattitude, date)

        return {
            "temp": receivedData["hourly"]["temperature_2m"][timefocusId],
            "rel_humidity": receivedData["hourly"]["relative_humidity_2m"][timefocusId],
            "rain": receivedData["hourly"]["rain"][timefocusId],
            "weather_code": receivedData["hourly"]["weather_code"][timefocusId],
            "cloud_cover": receivedData["hourly"]["cloud_cover"][timefocusId],
            "wind_speed": receivedData["hourly"]["wind_speed_10m"][timefocusId],
            "soil_moisture": receivedData["hourly"]["soil_moisture_0_to_7cm"][timefocusId],
            "daylight_duration": receivedData["daily"]["daylight_duration"][0],
            "sunshine_duration": receivedData["daily"]["sunshine_duration"][0]
            }
    
    def storeDataset(self, df_weather):
        print("Saving latest state of dataset")
        print(df_weather.head())

        with open(Config.weatherDataframeFilepath, 'wb') as pickleFile:
            pickle.dump(df_weather, pickleFile, protocol=pickle.HIGHEST_PROTOCOL)
    
    def getWeatherForSurvey(self, startId) -> pd.DataFrame:
    
        if not os.path.isfile(Config.surveyDataframeFilepath):
            raise IOError(f"Could not find dataset under {Config.surveyDataframeFilepath} please provide, or run SurveyHandling pipeline before.")    
        if not os.path.isfile(Config.songAttributesDataframeFilepath):
            raise IOError(f"Missing {Config.songAttributesDataframeFilepath}, please run SongAttributes extraction before WeatherRequests since it manipulates the number of cases." )
        
        with open(Config.surveyDataframeFilepath, 'rb') as pickleFile:
            df_survey = pickle.load(pickleFile)
        with open(Config.songAttributesDataframeFilepath, "rb") as pickleFile:
            df_songFeatures = pickle.load(pickleFile)
        
        df_survey_streamlined = df_survey.loc[
            (df_survey["artist_name"].isin(df_songFeatures["artist_name"])) &
            (df_survey["track_title"].isin(df_songFeatures["track_title"]))
            ]
        df_surveyFeatures = pd.merge(df_survey_streamlined, df_songFeatures)
                                              
        weatherData = {
            "tweet_longitude": [], 
            "tweet_latitude": [], 
            "tweet_datetime": [], 
            "temp":[],
            "rel_humidity": [],
            "rain": [],
            "weather_code": [],
            "cloud_cover": [],
            "wind_speed": [],
            "soil_moisture": [],
            "daylight_duration": [],
            "sunshine_duration": []
            }
        completedDataset = True
        for idr, values in enumerate(df_surveyFeatures.get(["tweet_longitude", "tweet_latitude", "tweet_datetime"]).values.tolist()[startId:]):
            curLongitude, curLatitude, curDate = values
            
            if idr > self._maxHourlyRequests:
                completedDataset = False
                break
            
            weather = self.getStatisticsFor(longitude=curLongitude, lattitude=curLatitude, date=curDate)
            weatherData["tweet_longitude"].append(curLongitude)
            weatherData["tweet_latitude"].append(curLatitude)
            weatherData["tweet_datetime"].append(curDate)
            for attribute in weather.keys():
                weatherData[attribute].append(weather[attribute])
        
        if not completedDataset:
            lastId = idr
            print(f"Reached hourly max requests limit (5000) of API provider. Try on more time today, as the max. daily limit is 10000. Start then from ID {lastId}.")
        
        return pd.DataFrame(weatherData)

if __name__ == "__main__":
    testlongitude = -50.531223
    testlattitude = -18.453224499999997
    testday = 15
    testmonth = 9

    print(f"This checks retrieving Weather Data on {testlongitude}:{testlattitude} on day {testday} month {testmonth}")

    weatherRequests = WeatherRequests()
    #stats = weatherRequests.getStatisticsFor(-50.531223, -18.453224499999997, 11, 2)

    #print ("Result is")
    #print(stats)
    df_weather = weatherRequests.getWeatherForSurvey(0)
    weatherRequests.storeDataset(df_weather)
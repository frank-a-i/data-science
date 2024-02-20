import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pickle
import requests
import datetime
import pandas as pd
from pipelines.common import Config, storeContent
from datetime import datetime

class WeatherRequests:
    def __init__(self):
        self._features = "hourly="
        self._features += "temperature_2m"
        self._features += ",relative_humidity_2m"
        self._features += ",rain"
        self._features += ",weather_code"
        self._features += ",cloud_cover"
        self._features += ",wind_speed_10m"
        self._features += "&daily="
        self._features += "daylight_duration"
        self._features += ",sunshine_duration"

        self._maxHourlyRequests = 5000
        self._maxDailyRequests = 10000
        self._urlPastWeatherApi = "https://archive-api.open-meteo.com/v1/archive"
        self._urlCurrentWeatherApi = "https://api.open-meteo.com/v1/forecast"

    def _requestData(self, longitude: float, latitude: float, queryDate: datetime) -> (int, dict):
        """ Retrieve local meterological information

        Args:
            longitude (float)
            latitude  (float)
            queryData (datetime): date for which the data should be extracted

        Returns:
            (int, dict): identifier to read the features at the right time spot, api resonse as a dict
        """
        apiDate = f"{queryDate.year}-{queryDate.month:02d}-{queryDate.day:02d}"
        
        timeRange = f"start_date={apiDate}&end_date={apiDate}"
        queryUrl = self._urlCurrentWeatherApi if queryDate.year >= 2024 else self._urlPastWeatherApi
        
        apiCmd = f"{queryUrl}?latitude={latitude}&longitude={longitude}&{self._features}&{timeRange}"
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
        date: datetime) -> dict:
        """ Get metrological data for geo-coordinates and date

        Args:
            longitude (float)
            lattitude (float)
            date (datetime)

        Returns:
            dict: meterological sample
        """

        timefocusId, receivedData = self._requestData(longitude, lattitude, date)

        return {
            "temp": receivedData["hourly"]["temperature_2m"][timefocusId],
            "rel_humidity": receivedData["hourly"]["relative_humidity_2m"][timefocusId],
            "rain": receivedData["hourly"]["rain"][timefocusId],
            "weather_code": receivedData["hourly"]["weather_code"][timefocusId],
            "cloud_cover": receivedData["hourly"]["cloud_cover"][timefocusId],
            "wind_speed": receivedData["hourly"]["wind_speed_10m"][timefocusId],
            "daylight_duration": receivedData["daily"]["daylight_duration"][0],
            "sunshine_duration": receivedData["daily"]["sunshine_duration"][0]
            }
    
    def statisticsToday(self,
                        longitude: float,
                        latitude: float):
        """ Returns today's meterological data for a geo-coodinate """
        stats = self.getStatisticsFor(longitude, latitude, datetime.now())
        return stats
    
    def getWeatherForSurvey(self) -> pd.DataFrame:
        """ Takes the survey location information and retrieves meterological data for the individual cases

        Raises:
            IOError: Stops if necessary data is not available

        Returns:
            pd.DataFrame: meterological data for each survey case
        """
    
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
            "daylight_duration": [],
            "sunshine_duration": []
            }
        completedDataset = True
        for idr, values in enumerate(df_surveyFeatures.get(["tweet_longitude", "tweet_latitude", "tweet_datetime"]).values.tolist()):
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
    print("[main] Fetching meterological features\n")
    weatherRequests = WeatherRequests()
    df_weather = weatherRequests.getWeatherForSurvey()
    storeContent(df_weather, Config.weatherDataframeFilepath, f"Saving latest state of dataset\n{df_weather.head()}")
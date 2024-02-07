import requests
from numpy import mean
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

        self._surveyYear = str(2012)
        self._urlWeatherApi = "https://archive-api.open-meteo.com/v1/archive"

    def _requestData(self, longitude: float, lattitude: float, day: int, month: int) -> dict:
        
        day = str(day).zfill(2)
        month = str(month).zfill(2)
        
        timeRange = f"start_date={self._surveyYear}-{month}-{day}&end_date={self._surveyYear}-{month}-{day}"
        apiCmd = f"{self._urlWeatherApi}?latitude={lattitude}&longitude={longitude}&{self._features}&{timeRange}"
        r = requests.get(apiCmd)

        return r.json()

    def getStatisticsFor(self,
        longitude: float,
        lattitude: float,
        day: int,
        month: int):

        receivedData = self._requestData(longitude, lattitude, day, month)

        return WeatherFeatures(
            SequenceFeature(receivedData["hourly"]["temperature_2m"]),
            SequenceFeature(receivedData["hourly"]["relative_humidity_2m"]),
            SequenceFeature(receivedData["hourly"]["rain"]),
            SequenceFeature(receivedData["hourly"]["weather_code"]),
            SequenceFeature(receivedData["hourly"]["cloud_cover"]),
            SequenceFeature(receivedData["hourly"]["wind_speed_10m"]),
            SequenceFeature(receivedData["hourly"]["soil_moisture_0_to_7cm"]),
            receivedData["daily"]["daylight_duration"][0],
            receivedData["daily"]["sunshine_duration"][0]
            )


if __name__ == "__main__":
    testlongitude = -50.531223
    testlattitude = -18.453224499999997
    testday = 15
    testmonth = 9

    print(f"This checks retrieving Weather Data on {testlongitude}:{testlattitude} on day {testday} month {testmonth}")

    weatherRequests = WeatherRequests()
    stats = weatherRequests.getStatisticsFor(-50.531223, -18.453224499999997, 11, 2)

    print ("Result is")
    print(stats)
import os
from dataclasses import dataclass

@dataclass
class GeoLocation:
    longitude: float
    latitude: float

class GeoArea:  # rectangle around europe
    def __init__(self, tl: GeoLocation, br: GeoLocation):
        self.topLeft = tl
        self.bottomRight = br

@dataclass
class Config:
    surveyDataframeFilepath: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "states", "survey_data.p")
    weatherDataframeFilepath: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "states", "weather_data.p")
    songAttributesDataframeFilepath: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "states", "song_attribute_data.p")
    songSearchResultsFilepath: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "states", "song_ids.csv")
    cleanSongSearchResultsFilepath: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "states", "clean_song_ids.csv")
    classifierFilepath: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "states", "clfs.p")
    rawDataPath: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dataset")
    testArea = GeoArea(tl=GeoLocation(-32.04, 71.89), br=GeoLocation(40.70, 33.83))
    apiRequestLimit = 5000
    
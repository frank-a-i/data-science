import os
import pickle
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
    fullDataframeFilepath: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "states", "full_data.p")
    songSearchResultsFilepath: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "states", "song_ids.csv")
    cleanSongSearchResultsFilepath: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "states", "clean_song_ids.csv")
    classifierFilepath: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "states", "clfs.p")
    rawDataPath: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dataset")
    testArea = GeoArea(tl=GeoLocation(-32.04, 71.89), br=GeoLocation(40.70, 33.83))
    songDescriptors = ['danceability', 'energy', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
       'valence', 'tempo']
    weatherDescriptors = ['temp', 'rel_humidity', 'rain', 'weather_code', 'cloud_cover', 'wind_speed', 'daylight_duration',
       'sunshine_duration']
    apiRequestLimit = 5000
    

def storeContent(data: Union[dict, pd.DataFrame], path: str, userMsg : str =""):
    """ Save results presistently

    Args:
        data    (Union[dict, pd.DataFrame]): expected is either the classifiers or the database
        path    (str): where the data should be stored to
        userMsg (str): a message that gets prompted before storing
    """
    
    if (len(userMsg) > 0):
        print(userMsg)

    with open(Config.classifierFilepath, 'wb') as pickleFile:
        pickle.dump(clfs, pickleFile, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"Stored content to {path}")
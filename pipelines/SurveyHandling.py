import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import zipfile
import glob
import wget
import os
import numpy as np
import pandas as pd
from datetime import datetime
from pipelines.common import Config, storeContent

class SurveyHandling:
    def __init__(self):
        self._datasetUrls=[
            "http://www.cp.jku.at/datasets/MMTD/tweet.zip",
            "http://www.cp.jku.at/datasets/MMTD/track.zip",
            "http://www.cp.jku.at/datasets/MMTD/artists.zip"
            ]
        
        self._prepareDataset()

    def _prepareDataset(self):
        """ Downloads, and extracts the data

        Raises:
            IOError: Stops if the necessary data is not present
        """
        searchAnyContentCmd = os.path.join(Config.rawDataPath, "*")
        target_content = glob.glob(searchAnyContentCmd)
        
        if not os.path.exists(Config.rawDataPath):
            raise IOError(f"Cannot find {Config.rawDataPath}")

        if len(target_content) > 1:
            print("Found non-empty target directory, skipping unpacking & overwriting")
            return
        
        for dset in self._datasetUrls:
            print(f"\nDownloading {dset}")
            wget.download(dset, out=Config.rawDataPath)
        print(f"Downloaded zipped dataset to {Config.rawDataPath}")

        zipfiles = [os.path.join(Config.rawDataPath, dset.split("/")[-1]) for dset in self._datasetUrls]
        for subsetfile in zipfiles:
            print(f"unpacking {subsetfile}")
            with zipfile.ZipFile(subsetfile, 'r') as compressedFile:
                compressedFile.extractall(Config.rawDataPath)
                
        print(f"Extracted {len(glob.glob(searchAnyContentCmd)) - 1} files to {Config.rawDataPath}")

    def composeDataframe(self, dropIdentifier=True) -> pd.DataFrame:
        """ Turns the individual raw datasets into a combined dataframe

        Args:
            dropIdentifier (bool, optional): whether the identifier columns should be kept, after they have been merged with the actual information (e.g. trackId -> track_title). Defaults to True.

        Raises:
            IOError: Stops if necessary data is not present

        Returns:
            pd.DataFrame: all raw datasets combined as a dataframe
        """
        foundFiles = [os.path.basename(curFile) for curFile in glob.glob(os.path.join(Config.rawDataPath, "*"))]
        requiredFiles = [(dset.split("/")[-1]).replace(".zip",".txt") for dset in self._datasetUrls]
        for dsetFile in requiredFiles:
            if dsetFile not in foundFiles:
                raise IOError(f"Missing essential data source '{dsetFile}', cannot proceed.")

        df_tweet = pd.read_csv(os.path.join(Config.rawDataPath, "tweet.txt"), delimiter="\t", on_bad_lines="warn")
        
        df_track = pd.read_csv(os.path.join(Config.rawDataPath, "track.txt"), delimiter="\t", on_bad_lines="warn")
        df_track.columns = ["tweet_trackId", "track_title", "tweet_artistId"]
        
        df_artist = pd.read_csv(os.path.join(Config.rawDataPath, "artists.txt"), delimiter="\t", on_bad_lines="warn")
        df_artist.columns = ["tweet_artistId", "artist_mbid", "artist_name"]
        
        df = df_tweet
        
        for subframe in [df_track, df_artist]:
            df = pd.merge(df, subframe)
        
        df = self._convertToAppropriateDatetype(df)
        df_europe = df.loc[(df["tweet_longitude"] > Config.testArea.topLeft.longitude) & 
                                      (df["tweet_longitude"] < Config.testArea.bottomRight.longitude) &
                                      (df["tweet_latitude"] > Config.testArea.bottomRight.latitude) & 
                                      (df["tweet_latitude"] < Config.testArea.topLeft.latitude)]
        
        df_reduced = df_europe.drop(np.random.choice(df_europe.index, df_europe.shape[0] - Config.apiRequestLimit, replace=False)).reset_index()

        if dropIdentifier:
            self._df = df_reduced.drop(["tweet_trackId", "tweet_artistId", "tweet_userId"], axis=1)
        else:
            self._df = df_reduced

        return self._df
    
    def _convertToAppropriateDatetype(self, df: pd.DataFrame) -> pd.DataFrame:
        """ Turns the raw-string information to the actual one

        Args:
            df (pd.DataFrame): the DataFrame with only str as cell dtype

        Returns:
            pd.DataFrame: the DataFrame with the right dtypes
        """
        
        df["tweet_datetime"] = df["tweet_datetime"].apply(lambda curDate: datetime.strptime(curDate, "%Y-%m-%d %H:%M:%S"))
        strToNumFields = ["tweet_longitude", "tweet_latitude", "tweet_trackId", "tweet_artistId",  "tweet_tweetId", "tweet_id", "tweet_weekday"]
        for field in strToNumFields:
            df[field] = pd.to_numeric(df[field])
            
        return df

    def generateInsights(self, df):
        """ Create statistics """

        print("Composing data, this might take some minutes")
        analyticsPath = os.path.join(Config.rawDataPath, "..", "analytics")

        print("Check for missing data")
        df.isnull().sum().to_csv(os.path.join(analyticsPath, "how_much_data_is_missing.csv"))

        print("Check for date of records distribution")
        dateCounts = df.get(["tweet_datetime"]).value_counts()
        dateCounts.to_csv(os.path.join(analyticsPath, "date_distribution.csv"))

        print("Check for artist distribution")
        artistCounts = df["artist_name"].value_counts()
        artistCounts.to_csv(os.path.join(analyticsPath, "artists_distribution.csv"))
        artistfig = artistCounts.loc[artistCounts > 3].plot.bar().get_figure() # refocusing for a better overview
        artistfig.set_size_inches(200,5)
        artistfig.savefig(os.path.join(analyticsPath, "artist_distribution.png"), bbox_inches='tight', dpi=200)

        print("Check for country distribution")
        ax = df.get(["tweet_latitude", "tweet_longitude"]).astype(float).plot.scatter(y="tweet_latitude", x="tweet_longitude", s=1) # refocusing for a better overview
        countryfig = ax.get_figure()
        countryfig.set_size_inches(10,10)
        ax.set_xlim(-180, 180)
        ax.set_ylim(-100, 100)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.set_title("Sample extraction location")
        countryfig.savefig(os.path.join(analyticsPath, "country_distribution.png"), bbox_inches='tight', dpi=200)

        print(f"Completed, see results under '{analyticsPath}'")   
    

if __name__=="__main__":
    print("[main] Reading survey data \n")
    surveyHandling = SurveyHandling()
    df = surveyHandling.composeDataframe(dropIdentifier=True)
    surveyHandling.generateInsights(df)
    storeContent(df, Config.surveyDataframeFilepath, f"Saving latest state of dataset\n{df.head()}")

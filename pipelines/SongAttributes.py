import requests
import os
import json
import pickle
import numpy as np
import pandas as pd
from typing import Union, Tuple
from time import sleep
from common import Config, storeContent
from dataclasses import dataclass


class SongAttributes:

    def __init__(self,  client_id="78388a06f8b342aca5c74bbc8bbad303",
                        client_pw="6addc5ea36654ef0ba38a29468d1e0d7"):

        self._client_id = client_id         # Spotify-API-ID
        self._client_pw = client_pw         # Spotify-API-PW
        self._token = None                  # Spotify-API-Token
        self._batchSize = 99                # limit set by API
        self._sleepBeforeNextAPIRequest = 1 # number of seconds to wait to relieve API
        self._countryCodes = ["US", "DE", "FR", "ES", "IT", "GB"] # list of country markets to search in for songs 

        self._retrieveAccessToken()         
        
    def _retrieveAccessToken(self):
        """ Generate new Spotify API access token
        Spotify requires frequently a newly generated token in order to interact with the API
        """
        r = requests.post(
            url='https://accounts.spotify.com/api/token', 
            headers={"Content-Type": "application/x-www-form-urlencoded"}, 
            data={"grant_type":"client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_pw})
        try:
            self._token = r.json()["access_token"]
        except Exception as e:
            print(f"Could not get API token:\n{e}")

    def _searchSong(self, title: str, market: str) -> Union[dict, None]:
        """ Query Spotify to get artist and spotify ID 

        Args:
            title (str): the song title to look for
            market (str): the country market where spotify should look

        Returns:
            Union[dict, None]: response of Spotify API
        """
        apiReadableTitle = title.replace(" ", "+").lower()
        sleep(self._sleepBeforeNextAPIRequest)  # destress API
        r = requests.get(
            url = f"https://api.spotify.com/v1/search?q={apiReadableTitle}&type=track&market={market}",
            headers = {"Authorization": f"Bearer {self._token}"}
        )
    
        response = None
        try:
             response = r.json()
        except Exception as e:
            print(f"Error: Could not get proper response, for\n{r}got\n{e}")
            
        return response

    def _retrieveSongAttributes(self, contentIds: list[str]) -> list[dict]:
        """ Get music descriptors for song

        Args:
            contentIds (list[str]): list of songs that should be evaluated

        Returns:
            list[dict]: spotify response
        """
        sleep(self._sleepBeforeNextAPIRequest)
        
        contentIdsStr = ""
        for contentId in contentIds:
            contentIdsStr = f"{contentIdsStr}%2C{contentId}"
        r = requests.get(
            url = f"https://api.spotify.com/v1/audio-features?ids={contentIdsStr}",
            headers = {"Authorization": f"Bearer {self._token}"}
        )
        
        response = None
        try:
            response = r.json()["audio_features"]
        except Exception as e:
            print(f"Error: Could not get proper response, for\n{r}got\n{e}")
        
        return response

    def _fetchSongId(self, requestedTitle: str, expectedArtist: str) -> Union[None, Tuple[contentId, popularity]]:
        """ Iterate through dataset and compose a dataset of song features and identification

        Args:
            requestedTitle (str): the title that should be looked for in Spotify
            expectedArtist (str): the artist that is used to identify the right track

        Returns:
            Union[None, Tuple[contentId, popularity]]: the identification and popularity feature
        """
        
        gotMatch = False
        for market in self._countryCodes:
            if gotMatch:
                break
            for _ in range(10, 0, -1): # straight retry
                searchResult = self._searchSong(requestedTitle, expectedArtist, market)
                if searchResult is None:
                    raise RuntimeError
                if "tracks" in searchResult.keys():
                    break
                if "error" in searchResult.keys() and searchResult["error"]["status"] == 401:  # refreshing s required by API
                    self._retrieveAccessToken()
            if "tracks" not in searchResult.keys(): # finaly give up
                print(f"Unexpected API response for {requestedTitle}  - {expectedArtist}\n{searchResult}")

            for item in searchResult["tracks"]["items"]:
                try:
                    for artist in item["artists"]: 
                        if artist["name"].lower() == expectedArtist.lower() and item["name"].lower() == requestedTitle.lower():
                            gotMatch = True
                            contentId = item["id"]
                            popularity = item["popularity"]
                            break
                    if gotMatch:
                        break
                except Exception as e:
                    print(f"Got incomplete Spotify Response for {requestedTitle} - {expectedArtist}\n{e}")
                    
        if gotMatch == False:
            return None
        else:
            return (contentId, popularity)
        
    def _fetchAttributes(self, df_content: pd.DataFrame) -> pd.DataFrame:
        """ Retrieve song features for each song

        Args:
            df_content (pd.DataFrame): the collection of songs

        Returns:
            pd.DataFrame: the attached song features
        """
        musicFeatures = {"id": []}
        for feature in Config.songDescriptors:
            musicFeatures.update({feature: []})
        
        batchProcessingIds = []
        for curContent in df_content.iterrows():
            if len(batchProcessingIds) < self._batchSize:
                batchProcessingIds.append(curContent[1]["id"])
                continue
            relatedAttributes = self._retrieveSongAttributes(batchProcessingIds)
            batchProcessingIds = []
            
            for songAttributes in relatedAttributes:
                if songAttributes is None:
                    continue
                trackFeatures = dict()
                for attribute in Config.songDescriptors:
                    musicFeatures[attribute].append(songAttributes[attribute] if attribute in songAttributes.keys() else 0)
                
                musicFeatures["id"].append(songAttributes["id"])

        return pd.DataFrame(musicFeatures)
   
    def getSongAttributesForSurvey(self):
        """ Iterate through dataset, figure out the contentId and related song descriptors

        This function takes a while, therefore and because Spotify API does not always work stable 
        an intermediate state is stored in Config.songSearchResultsFilepath to continue until it is finished.

        This function will only query song data that have not been retrieved yet, even after a break. So this 
        function can be called as many times it is necessary.
        """
        
        with open(Config.surveyDataframeFilepath, 'rb') as pickleFile:
            df = pickle.load(pickleFile)
        
        df_music = df.get(["track_title", "artist_name"])
        
        headline="artist_name;track_title;id;popularity"
        df_storedIds = None
        if os.path.isfile(Config.songSearchResultsFilepath):
            try:
                df_storedIds = pd.read_csv(Config.songSearchResultsFilepath, delimiter=";")
            except pd.errors.EmptyDataError:
                df_storedIds = pd.DataFrame({"artist_name":[], "track_title":[], "title":[], "id":[], "popularity":[]})
            except Exception as e:
                print(e)
        else:
            with open(Config.songSearchResultsFilepath, 'w') as newSongIdFile:
                newSongIdFile.write(headline)
                
        with open(Config.songSearchResultsFilepath, 'a') as songIdFile:
            for idt, track in enumerate(df_music.iterrows()):
                if idt % 1 == 0:
                    print(f"Processed {idt}/{df_music.shape[0]}")
    
                artist = track[1]["artist_name"]
                title = track[1]["track_title"]
                df_relevantContent = df_storedIds.loc[(df_storedIds["artist_name"] == artist) & (df_storedIds["track_title"] == title)]
                alreadyFetched = df_relevantContent.shape[0] > 0

                if alreadyFetched:
                    continue
                idAndPopularity = self._fetchSongId(title, artist)
                
                if idAndPopularity is None:
                    curId = np.nan
                    curPopularity = np.nan
                else:
                    curId = idAndPopularity[0]
                    curPopularity = idAndPopularity[1]
                df_storedIds = pd.concat([
                    df_storedIds,
                    pd.DataFrame({f"{headline.split(';')[0]}": [artist], 
                                  f"{headline.split(';')[1]}": [title], 
                                  f"{headline.split(';')[2]}": [curId], 
                                  f"{headline.split(';')[3]}": [curPopularity]})])
                newEntry=f"{artist};{title};{curId};{curPopularity}\n"
                print(f"Adding {newEntry}")
                songIdFile.write(newEntry)
                
        print("Number of total findings: ", df_storedIds.shape[0])
        df_dropNone = df_storedIds.loc[df_storedIds.get(["id", "popularity"]).notna().all(axis=1)]
        print("Number of identified songs: ", df_dropNone.shape[0])
        df_uniqueIds = df_dropNone.drop_duplicates()
        print("Number of unique identified songs: ", df_uniqueIds.shape[0])
        df_orderedUniqueIds = df_uniqueIds.reset_index(drop=True)
        print("Storing results to: ", Config.cleanSongSearchResultsFilepath)
        df_orderedUniqueIds.to_csv(Config.cleanSongSearchResultsFilepath)
        df_musicFeatures = self._fetchAttributes(df_orderedUniqueIds.get(["id", "popularity"]))
        df_allSongInfo = pd.merge(df_orderedUniqueIds, df_musicFeatures).drop(["popularity"], axis=1)  # covered in df_musicFeatures

        storeContent(df_allSongInfo, Config.songAttributesDataframeFilepath, df_allSongInfo.head())
        

if __name__== "__main__":
    
    songAttributes = SongAttributes()
    songAttributes.getSongAttributesForSurvey()
import requests
import json
from dataclasses import dataclass

@dataclass
class SongFeatures:
    title: str
    artist: str
    contentId: str
    popularity: int
    attributes: dict


class SongAttributes:

    def __init__(self,  client_id="78388a06f8b342aca5c74bbc8bbad303",
                        client_pw="070ad73161214a8797acab95ad1f91d1"):

        self._client_id = client_id
        self._client_pw = client_pw
        self._token = self._retrieveAccessToken()

    def _retrieveAccessToken(self) -> str:
        r = requests.post(
            url='https://accounts.spotify.com/api/token', 
            headers={"Content-Type": "application/x-www-form-urlencoded"}, 
            data={"grant_type":"client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_pw})
        return r.json()["access_token"]

    def _searchSong(self, title: str, artist: str):
        apiReadableTitle = title.replace(" ", "+")
        r = requests.get(
            url = f"https://api.spotify.com/v1/search?q={apiReadableTitle}&type=track",
            headers = {"Authorization": f"Bearer {self._token}"}
        )
        return r.json()

    def _retrieveSongAttributes(self, contentId):
        r = requests.get(
            url = f"https://api.spotify.com/v1/audio-features/{contentId}",
            headers = {"Authorization": f"Bearer {self._token}"}
        )
        return r.json()

    def getSongFeatures(self, requestedTitle: str, expectedArtist: str):
        searchResult = self._searchSong(requestedTitle, expectedArtist)
        
        
        gotMatch = False
        for item in searchResult["tracks"]["items"]:
            for artist in item["artists"]: 
                if artist["name"] == expectedArtist and item["name"] == requestedTitle:
                    gotMatch = True
                    contentId = item["id"]
                    popularity = item["popularity"]
                    break

        if gotMatch == False:
            raise RuntimeError("Could not find expected title '{requestedTitle}' by '{expectedArtist}'")

        relatedAttributes = self._retrieveSongAttributes(contentId)
        keepAttributes = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
        trackFeatures = dict()
        for attribute in keepAttributes:
            trackFeatures.update({attribute: relatedAttributes[attribute]})
        return SongFeatures(requestedTitle, expectedArtist, contentId, popularity, trackFeatures)

if __name__== "__main__":
    testTrack = "Life in Technicolor"
    testArtist = "Coldplay"

    print(f"This tests the functionality with '{testTrack}' by '{testArtist}'")
    songAttributes = SongAttributes()
    feats = songAttributes.getSongFeatures(testTrack, testArtist)
    
    print(f"The retrieved data to this song looks like:")
    print(feats)
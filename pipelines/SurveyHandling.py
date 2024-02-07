import zipfile
import glob
import wget
import os
import pandas as pd


class SurveyHandling:
    def __init__(self, target=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dataset")):
        self._datasetUrl="http://www.cp.jku.at/people/schedl/data/MusicMicro/11.11-09.12/musicmicro.zip"
        self._target = target

        self._prepareDataset()

    def _prepareDataset(self):
        searchAnyContentCmd = os.path.join(self._target, "*")
        target_content = glob.glob(searchAnyContentCmd)
        
        if not os.path.exists(self._target):
            raise IOError(f"Cannot find {self._target}")

        if len(target_content) > 0:
            print("Found non-empty target directory, skipping unpacking & overwriting")
            return
        
        wget.download(self._datasetUrl, out=self._target)
        print(f"Downloaded zipped dataset to {self._target}")

        with zipfile.ZipFile(os.path.join(self._target, self._datasetUrl.split("/")[-1]), 'r') as compressedFile:
            compressedFile.extractall(self._target)

        print(f"Extracted {len(glob.glob(searchAnyContentCmd)) - 1} files to {self._target}")

    def composeDataframe(self):
        foundFiles = [os.path.basename(curFile) for curFile in glob.glob(os.path.join(self._target, "*.txt"))]
        requiredFiles = ["artist_mapping.txt", "city_mapping.txt", "country_mapping.txt", "listening_data.txt", "track_mapping.txt"]
        for dsetFile in requiredFiles:
            if dsetFile not in foundFiles:
                raise IOError(f"Missing essential data source '{dsetFile}', cannot proceed.")

        df_listening = pd.read_csv(os.path.join(self._target, "listening_data.txt"), delimiter = "\t")
        df_track = pd.read_csv(os.path.join(self._target, "track_mapping.txt"), delimiter = "\t")
    

if __name__=="__main__":
    surveyHandling = SurveyHandling()
    surveyHandling.composeDataframe()
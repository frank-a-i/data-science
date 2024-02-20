import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pickle
import pandas as pd
from pipelines.common import Config, storeContent

from sklearn.tree import DecisionTreeRegressor as Regressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import root_mean_squared_error as rmse

def getData():
    """ Extract and combine the data from all previous processing

    Raises:
        IOError: won't continue if not all required df are loadable

    Returns:
        pd.DataFrame: the full dataset of all dataframes combined
    """
    
    for requiredFile in [Config.surveyDataframeFilepath, Config.songAttributesDataframeFilepath, Config.weatherDataframeFilepath]:
        if not os.path.isfile(requiredFile):
            raise IOError(f"Could not find preprocessed dataset under {requiredFile} please provide, or run SurveyHandling, SongAttributes, WeatherRequests pipeline before.")

    with open(Config.songAttributesDataframeFilepath, 'rb') as pickleFile:
        df_songAttributes = pickle.load(pickleFile)
    with open(Config.weatherDataframeFilepath, 'rb') as pickleFile:
        df_weatherAttributes = pickle.load(pickleFile)
    with open(Config.surveyDataframeFilepath, 'rb') as pickleFile:
        df_survey = pickle.load(pickleFile)
    
    df_survey_streamlined = df_survey.loc[
        (df_survey["artist_name"].isin(df_songAttributes["artist_name"])) &
        (df_survey["track_title"].isin(df_songAttributes["track_title"]))
        ]
    df_surveyFeatures = pd.merge(df_survey_streamlined, df_songAttributes)
    
    return pd.merge(df_surveyFeatures, df_weatherAttributes)


def trainRegressor(df: pd.DataFrame, clfs: dict, clfCase: str):
    """ Train a regressor and store it along its performance information

    Args:
        df (pd.DataFrame): the database to train the regressor
        clfs (dict): common dictionary to store the results
        clfCase (str): identifier that maps one individual song feature
    """
    X_train, X_test, y_train, y_test = train_test_split(df.get(Config.weatherDescriptors), df[clfCase], test_size=0.33, random_state=3)
   
    parameters = {
            "criterion": ["squared_error", "friedman_mse", "absolute_error", "poisson"],
            "splitter": ["best", "random"],
            "max_depth": range(1, 20),
            "min_samples_split": range(2, 10),
            "max_features": range(1, len(X_train.columns))
        }

    # optimize
    cv = GridSearchCV(Regressor(), param_grid=parameters)
    # train
    cv.fit(X_train, y_train)
    
    y_pred = cv.predict(X_test)
    error = rmse(y_test, y_pred)
    print(clfCase, error)
    clfs.update({clfCase: {"clf": cv, "error": error}})

def runAnalytics(df: pd.DataFrame):
    """Aquire regressors

    Args:
        df (pd.DataFrame): the database with weather and music features
    """

    clfs = dict()
    for clfCase in Config.songDescriptors:
        clfs.update({clfCase: None})
    
    for clfCase in Config.songDescriptors:
        print(f"Training {clfCase} regressor now")
        trainRegressor(df, clfs, clfCase)
    print("Finished training")
    
    storeContent(clfs, Config.classifierFilepath)
        
if __name__ == "__main__":
    print("[main] Drawing conclusions, training regressors \n")
    df = getData()
    storeContent(df, Config.fullDataframeFilepath)
    runAnalytics(df)
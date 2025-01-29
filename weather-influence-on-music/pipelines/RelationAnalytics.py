import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pipelines.common import Config, storeContent

from sklearn.tree import plot_tree
from sklearn.tree import DecisionTreeRegressor as Regressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import root_mean_squared_error as rmse
from sklearn.metrics import max_error

def cleanData(df: pd.DataFrame) -> pd.DataFrame:
    """ Inspecting and cleaning missing values

    Args:
        df (pd.DataFrame): the original df

    Returns:
        pd.DataFrame: the cleaned df
    """

    print(f"Cleaning dataframe with {df.shape[0]} samples.")
    df_cleaned = df.dropna(axis=1)
    print(f"Continuing with {df_cleaned.shape[0]} samples.")
    return df_cleaned

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
    
    return cleanData(pd.merge(df_surveyFeatures, df_weatherAttributes))

def generateTrainingInsights(case, clf, features):
    """ Print and plot training insights

    Args:
        case: what regressor is analysed
        clf: the regressor object
        features: list of features used in training
    """

    print(f"Evaluating {case}")
    print(f"Best tree parameters: {clf.best_params_}")
    importances = clf.best_estimator_.feature_importances_
    feature_indices = np.argsort(importances)
    importance_dict = {features[index]: importances[index] for index in feature_indices}
    print(f"Feature importance: {importance_dict}\n")

    fig, ax = plt.subplots()
    ax.barh(range(len(importances)), importances[feature_indices])
    ax.set_yticks(range(len(importances)))
    _ = ax.set_yticklabels(np.array(features)[feature_indices])
    ax.set_title(case)
    fig.set_size_inches(7,5)
    fig.savefig(os.path.join(Config.analyticsPath, f"feature_importance_{case}.png"), bbox_inches='tight')

def generateFeatureInsights(df: pd.DataFrame):
    """ Create statistics """
    
    print("Generating insights")
    # weather statistics
    fig, axes = plt.subplots(1, len(Config.weatherDescriptors))
    for idx, ax in enumerate(axes):
        ax.violinplot(df[Config.weatherDescriptors[idx]], showmedians=True)
        ax.set_title(Config.weatherDescriptors[idx])
    fig.set_size_inches(20,10)
    fig.savefig(os.path.join(Config.analyticsPath, "weather_descriptor_distribution_violinplot.png"), bbox_inches='tight', dpi=200)
    fig, axes = plt.subplots(1, len(Config.weatherDescriptors))
    for idx, ax in enumerate(axes):
        ax.boxplot(df[Config.weatherDescriptors[idx]])
        ax.set_title(Config.weatherDescriptors[idx])
    fig.set_size_inches(20,10)
    fig.savefig(os.path.join(Config.analyticsPath, "weather_descriptor_distribution_boxplot.png"), bbox_inches='tight', dpi=200)

    # song features
    fig, axes = plt.subplots(1, len(Config.songDescriptors))
    for idx, ax in enumerate(axes):
        ax.violinplot(df[Config.songDescriptors[idx]], showmedians=True)
        ax.set_title(Config.songDescriptors[idx])
    fig.set_size_inches(20,10)
    fig.savefig(os.path.join(Config.analyticsPath, "song_descriptor_distribution_violinplot.png"), bbox_inches='tight', dpi=200)
    fig, axes = plt.subplots(1, len(Config.songDescriptors))
    for idx, ax in enumerate(axes):
        ax.boxplot(df[Config.songDescriptors[idx]])
        ax.set_title(Config.songDescriptors[idx])
    fig.set_size_inches(20,10)
    fig.savefig(os.path.join(Config.analyticsPath, "song_descriptor_distribution_boxplot.png"), bbox_inches='tight', dpi=200)


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
    
    gsClf = GridSearchCV(Regressor(), param_grid=parameters, n_jobs=-1)
    # train
    gsClf.fit(X_train, y_train)
    
    y_pred = gsClf.predict(X_test)
    rmse_err = rmse(y_test, y_pred)
    max_err = max_error(y_test, y_pred)
    print(f"{clfCase} RMSE={rmse_err} max. error={max_err}")
    clfs.update({clfCase: {"clf": gsClf, "error": rmse_err}})

    generateTrainingInsights(clfCase, gsClf, X_train.columns)

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
    
    generateFeatureInsights(df)
    storeContent(clfs, Config.classifierFilepath)
        
if __name__ == "__main__":
    print("[main] Drawing conclusions, training regressors \n")
    df = getData()
    storeContent(df, Config.fullDataframeFilepath)
    runAnalytics(df)
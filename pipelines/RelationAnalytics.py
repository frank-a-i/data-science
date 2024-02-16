import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from common import Config

#from sklearn.svm import SVR as Regressor
from sklearn.tree import plot_tree
from sklearn.tree import DecisionTreeRegressor as Regressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import root_mean_squared_error as rmse

def getData():
    
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
        
def storeClassifier(clfs: dict):
    
    with open(Config.classifierFilepath, 'wb') as pickleFile:
        pickle.dump(clfs, pickleFile, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"Stored classifier to {Config.classifierFilepath}")

def trainRegressor(df, clfs, clfCase):
    X_train, X_test, y_train, y_test = train_test_split(df.get(['temp', 'rel_humidity', 'rain', 'weather_code',
       'cloud_cover', 'wind_speed', 'soil_moisture', 'daylight_duration',
       'sunshine_duration']), df[clfCase], test_size=0.33, random_state=3)
   
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
    
    
    #clf = Regressor(max_depth=2)
    #clf.fit(X_train, y_train)
    clf = cv
    y_pred = clf.predict(X_test)
    error = rmse(y_test, y_pred)
    print(clfCase, rmse)
    clfs.update({clfCase: {"clf": clf, "error": error}})

def runAnalytics(df: pd.DataFrame):
    
    """
    print(df.columns)
    x = []
    y = []
    z = []
    for row in df.iterrows():
        case = row[1]
        x.append(case["energy"])
        y.append(case["rel_humidity"])
        z.append(case["temp"])
        
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.scatter(x,y,z)
    plt.show()
    """
    clfs = dict()
    classifierCases = ['danceability', 'energy', 'key', 'loudness',
       'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
       'valence', 'tempo']
    for clfCase in classifierCases:
        clfs.update({clfCase: None})
    
    trainings = []
    for clfCase in classifierCases:
        print(f"Training {clfCase} regressor now")
        trainRegressor(df, clfs, clfCase)
    print("Finished training")
    
    storeClassifier(clfs)
    #plt.figure(figsize=(30, 30))
    #plot_tree(clf, feature_names=X_train.columns, filled=True)
    #plt.show()
    
    
    
        
if __name__ == "__main__":
    df = getData()
    runAnalytics(df)
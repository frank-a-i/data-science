from UI import app
import pickle
import numpy as np
import pandas as pd
from pipelines.common import Config
from pipelines.WeatherRequests import WeatherRequests
from flask import render_template, request#, url_for, , send_from_directory

weatherRequests = WeatherRequests()

with open(Config.fullDataframeFilepath, 'rb') as pickleFile:
    DF = pickle.load(pickleFile)
with open(Config.classifierFilepath, 'rb') as pickleFile:
    REGRESSORS = pickle.load(pickleFile)

# web pages
@app.route('/')
@app.route('/recommendation')
def recommendations():
    return render_template('recommendation.html')

@app.route('/insights')
def insights():
    return render_template('insights.html')

@app.route('/getWeather', methods=['POST'])
def getWeather():
    return weatherRequests.statisticsToday(
        longitude = request.form.get("long"),
        latitude = request.form.get("lat"))

@app.route('/getEstimateErrors', methods=["GET"])
def getEstimateErrors():
    return {feature: round(REGRESSORS[feature]["error"], 1) for feature in REGRESSORS.keys()}

@app.route('/getRecommendationStatistics', methods=['POST'])
def getSongStats():    
    results = {}
    for feature in REGRESSORS.keys():
        
        sample = pd.DataFrame(
            {feature: [request.form.get(feature)] for feature in [
                "temp", "rel_humidity", "rain", "weather_code", "cloud_cover", 
                "wind_speed", "soil_moisture", "daylight_duration", "sunshine_duration"]
             })
        
        estimate = REGRESSORS[feature]["clf"].predict(sample)[0]
        results.update({feature: round(estimate*100, 1) if feature not in ["tempo"] else round(estimate)})
        
    return results

@app.route('/getSongIdea', methods=['POST'])
def getSongIdea(tol=0.1):
    
    df_similarSongs = DF
    
    for feature in Config.songDescriptors:
        enabled = request.form.get(f"{feature}[enabled]")
        value = request.form.get(f"{feature}[value]")
        
        if (enabled):
            df_similarSongs = df_similarSongs.loc[(DF[feature] >= value - tol) & (DF[feature] <= value + tol)]

    nSamples = 3 if df_similarSongs.shape[0] >= 3 else df_similarSongs.shape[0]
    sample = df_similarSongs.sample(nSamples).get(["artist_name", "track_title"])
    return {"artist": [sample["artist_name"].values[idt] for idt in range(sample.shape[0])], 
            "title": [sample["track_title"].values[idt] for idt in range(sample.shape[0])]}
    
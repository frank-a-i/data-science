export function fillWeatherData(response) {
    document.getElementById('temp2mid').value = response["temp"];
    document.getElementById('relHum2mid').value = response["rel_humidity"];
    document.getElementById('rainid').value = response["rain"];
    document.getElementById('weatherCodeid').value = response["weather_code"];
    document.getElementById('cloudCoverid').value = response["cloud_cover"];
    document.getElementById('windSpeed10mid').value = response["wind_speed"];
    document.getElementById('daylightDurationid').value = response["daylight_duration"];
    document.getElementById('sunshineDurationid').value = response["sunshine_duration"];
}

function setProgress(id, updateLevel) {
    let element = document.getElementById(id);
    let elementLabel = document.getElementById(id + "Label");

    element.style.width = updateLevel + '%';
    element.setAttribute('aria-valuenow', updateLevel);
    elementLabel.innerText = elementLabel.innerText.split(":")[0] + " : " + updateLevel;
}

export function updateEstimateErrors(response) {
    document.getElementById("progressDanceabilityLabel").innerText += " (RMSE=" + response["danceability"] + ")";
    document.getElementById("progressEnergyLabel").innerText += " (RMSE=" + response["energy"] + ")";
    document.getElementById("progressModeLabel").innerText += " (RMSE=" + response["mode"] + ")";
    document.getElementById("progressLoudnessLabel").innerText += " (RMSE=" + response["loudness"] + ")";
    document.getElementById("progressAcousticnessLabel").innerText += " (RMSE=" + response["acousticness"] + ")";
    document.getElementById("progressSpeechinessLabel").innerText += " (RMSE=" + response["speechiness"] + ")";
    document.getElementById("progressInstrumentalnessLabel").innerText += " (RMSE=" + response["instrumentalness"] + ")";
    document.getElementById("progressLivenessLabel").innerText += " (RMSE=" + response["liveness"] + ")";
    document.getElementById("progressValenceLabel").innerText += " (RMSE=" + response["valence"] + ")";
    document.getElementById("progressTempoLabel").innerText += " (RMSE=" + response["tempo"] + ")";
}

export function fillRecommendationBars(response) {
    setProgress("progressDanceability", response["danceability"]);
    setProgress("progressEnergy", response["energy"]);
    setProgress("progressMode", response["mode"]);
    setProgress("progressLoudness", response["loudness"]);
    setProgress("progressAcousticness", response["acousticness"]);
    setProgress("progressSpeechiness", response["speechiness"]);
    setProgress("progressInstrumentalness", response["instrumentalness"]);
    setProgress("progressLiveness", response["liveness"]);
    setProgress("progressValence", response["valence"]);
    setProgress("progressTempo", response["tempo"]);
}

export function fillSongId(response) {

    var rowsToFill = 3
    if (response["title"].length < 3) {
        $("#thirdSongId").hide();
        rowsToFill--;
    }
    else {
        $("#thirdSongId").show();
    }

    if (response["title"].length < 2) {
        $("#secondSongId").hide();
        rowsToFill--;
    }
    else {
        $("#secondSongId").show();
    }

    if (response["title"].length < 1) {
        document.getElementById("firstSongId").innerText = "Found no matching song";
    }
    else {
        document.getElementById("firstSongId").innerText = response["artist"][0] + " - " + response["title"][0];
        if (rowsToFill >= 2) {
            document.getElementById("secondSongId").innerText = response["artist"][1] + " - " + response["title"][1];
        }
        if (rowsToFill >= 3) {
            document.getElementById("thirdSongId").innerText = response["artist"][2] + " - " + response["title"][2];
        }
    }
}
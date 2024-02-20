import { fillWeatherData, updateEstimateErrors, fillRecommendationBars, fillSongId } from "./callbacks.js";

$(document).ready(function () {
    // feed in user input for evaluation, eventually update visuals
    $("#getWeatherStats").click(function (event) {
        $.ajax({
            type: 'POST',
            url: "/getWeather",
            data: {
                "lat": document.getElementById('latitudei').value,
                "long": document.getElementById('longitudei').value
            },
            success: fillWeatherData
        });

        $("#weatherStatsContainer").show();
        $("#getRecommendationStats").show();
    });

    $("#getRecommendationStats").click(function (event) {
        $.ajax({
            type: 'POST',
            url: "/getRecommendationStatistics",
            data: {
                "temp": document.getElementById('temp2mid').value,
                "rel_humidity": document.getElementById('relHum2mid').value,
                "rain": document.getElementById('rainid').value,
                "weather_code": document.getElementById('weatherCodeid').value,
                "cloud_cover": document.getElementById('cloudCoverid').value,
                "wind_speed": document.getElementById('windSpeed10mid').value,
                "daylight_duration": document.getElementById('daylightDurationid').value,
                "sunshine_duration": document.getElementById('sunshineDurationid').value,
                "soil_moisture": 0
            },
            success: fillRecommendationBars
        });
        $("#progressContainer").show();
        $("#giveSongExample").show();
        $("#checkboxContainer").show();
    });

    $.ajax({
        type: 'GET',
        url: "/getEstimateErrors",
        success: updateEstimateErrors
    });

    $("#giveSongExample").click(function (event) {
        $.ajax({
            type: 'POST',
            url: "/getSongIdea",
            data: {
                "danceability": {
                    "enabled": document.getElementById('checkDanceability').value,
                    "value": document.getElementById("progressDanceabilityLabel").innerText.split(" ")[2]
                },
                "energy": {
                    "enabled": document.getElementById('checkEnergy').value,
                    "value": document.getElementById("progressEnergyLabel").innerText.split(" ")[2]
                },
                "mode": {
                    "enabled": document.getElementById('checkMode').value,
                    "value": document.getElementById("progressModeLabel").innerText.split(" ")[2]
                },
                "tempo": {
                    "enabled": document.getElementById('checkTempo').value,
                    "value": document.getElementById("progressTempoLabel").innerText.split(" ")[2]
                },
                "loudness": {
                    "enabled": document.getElementById('checkLoudness').value,
                    "value": document.getElementById("progressLoudnessLabel").innerText.split(" ")[2]
                },
                "acousticness": {
                    "enabled": document.getElementById('checkAcousticness').value,
                    "value": document.getElementById("progressAcousticnessLabel").innerText.split(" ")[2]
                },
                "speechiness": {
                    "enabled": document.getElementById('checkSpeechiness').value,
                    "value": document.getElementById("progressSpeechinessLabel").innerText.split(" ")[2]
                },
                "instrumentalness": {
                    "enabled": document.getElementById('checkInstrumentalness').value,
                    "value": document.getElementById("progressInstrumentalnessLabel").innerText.split(" ")[2]
                },
                "liveness": {
                    "enabled": document.getElementById('checkLiveness').value,
                    "value": document.getElementById("progressLivenessLabel").innerText.split(" ")[2]
                },
                "valence": {
                    "enabled": document.getElementById('checkValence').value,
                    "value": document.getElementById("progressValenceLabel").innerText.split(" ")[2]
                }
            },
            success: fillSongId
        });
        $("#songContainer").show();
    });


    $("#progressContainer").hide();
    $("#weatherStatsContainer").hide();
    $("#getRecommendationStats").hide();
    $("#checkboxContainer").hide();
    $("#giveSongExample").hide();
    $("#songContainer").hide();

});
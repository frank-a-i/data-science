# Weather influence on music

## Purpose

Music, like art, lies in the eye of the beholder. Estimating what songs a person likes can be considered as a non-trivial task. Even under a genre usually prefered by the individual, the hit rate could often fall short of expectations of any recommendation. The reason someone is skipping a track may have various reasons. One could not be in the mood, listen too frequently to it, or listens to it the first time, or simply doesn't match one's taste, to name a few. Still there are many platforms with a business plan of selling music via streaming or as a album retailer. In order to improve the user experience, recommendation strategies have to be implemented, in order to avoid annoying the user by constantly advertising unrelated content.

This study considers retrieving such recommendation hints, based on meterological events. As the weather takes influence on humans, at least on the mood, it probably also has consequences on wether we rather would like to tune in to something relaxing or more powerfull. 

## Strategy and learning target

The [Million Musical Tweets Dataset](http://www.cp.jku.at/datasets/MMTD/) composed by the Johannes Kepler University of Linz gathered many broadcasted messages of individuals, containing what they are listening to. Along the title and artist, there's also listed the location, date and time.

This location and timing information then can be used to look up historical meterological data with the help of [Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api/).

These two data sources, are yet not enough. In order to give more general estimates, a third one is required describing these songs. As each individual comes with a different taste in music, it's rather difficult to directly take these titles as a learning target. Though if the music attributes can be described on a more abstract level, this information could then be taken to look up suggestions in the scope of the individual's preferences. That's where the [Spotify API](https://developer.spotify.com/documentation/web-api) comes in handy, which provides information like how *danceable* or *speechy* a track is.

## Data Acquistion

A million musical tweets is a relatively big data basis. When each of these samples would be analyzed it would overstrain the basic usage plan of the APIs. Upgrading the API-plan certainly would solve that, however for a proof of concept this might not be necessary. To put it in perspective, here's an overview from where in the world data has been collected

<img src="./analytics/general_country_distribution.png" alt="Overview to which area the samples of the whole MMTD relate to" style="width:70%;"/>

Hence in order to keep a certain diversity in the result and not being to focused on a specific group of people, for this research a subset was created containing the data from the european area. This area was choosen as it comes with two advantages: 

- within this area a large amount of completely different cultures can be found 
- the meterological situations are very different from country to country

In other words this covers a big variety to draw conclusions from, to eventually give better generalized estimates. In the following picture the locations are shown, of the samples that are actually used for evaluation.

<img src="./analytics/country_distribution.png" alt="Overview to which area the samples of the european area subset" style="width:70%;"/>

HOW IS THE FINAL DATASET COMPOSED

## Data inspection & training

### Artists 

![Distribution of artists](./analytics/artist_distribution.png)

### Song descriptors

![Distribution of song descriptors](./analytics/song_descriptor_distribution.png)

### Weather descriptors

![Distribution of weather descriptors](./analytics/weather_descriptor_distribution.png)

### Training strategy

## Results & Outlook

### A/B Tsting

### Further optimization
optimierung:
training mit geodaten
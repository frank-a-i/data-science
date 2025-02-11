# Disaster response analysis helper

This app analyses arbitrary text messages whether they are relevant for disaster emergency handling and puts it with the help of AI into relevant categories (like `missing people`, `child alone` or `food`) for a potential quicker processing and responding of a human operator.

It is based on a dataset with arbitrary and emergency messages. These first have to be preprocessed and turned into a machine processible format, after that classifiers are trained to separated arbitrary from relevant messages. 

In order to keep it interactive a web app is provided, demonstrating the capabilities and feeding own arbitrary messages for analysis

**Note:** It operates on an ensemble of Random Forest Classifiers in order to rapidly create a prototype. The accuracy could greatly be increased by tweaking the classification approach, though this was not the prime focus it was mainly about establishing a feasability PoC.

## How to run

Running from scratch one needs to 

0. Create virtual environment (use the top level `requirements.txt` for package list)

1. Compose the dataset by `python pipelines/etl.py`
2. Compose the classifier `python pipelines/ml.py`
3. Run the interface `python web_interface.py` and follow the instructions on the console output

As a shortcut, 1. and 2. can be skipped when `ressources/classifier.pkl` exists.

## Structure

This program needs an offline preparation before first usage. This is covered in the `pipelines` directory, where 

- `etl.py` extracts data and composes a dataset
- `ml.py` utilizes that dataset for preparing and training classifiers

Further files are for maintaining the UI

- `web_interface.py` and `UI.py` for running the `Flask` environment
- `analyzer.py` as used as an helper interface for the classifier

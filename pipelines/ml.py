
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import confusion_matrix

from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
import os
import sys
import pickle
import pandas as pd
import numpy as np
import argparse

nltk.download(['punkt', 'wordnet'])
def loadDataset(
    sqliteFile: str = f'sqlite:///{os.path.join(os.path.dirname(os.path.realpath(__file__)),  "..", "ressources", "disaster_response_data.db")}', 
    table: str = "Dataset") -> pd.DataFrame:
    """ Load the prepared dataset

    Args:
        sqliteFile (_type_, optional): path to the sqlite dataset.
        table (str, optional): name of sqlite table.

    Returns:
        pd.DataFrame: a dataframe converted from the database
    """
    return pd.read_sql_table(table, sqliteFile )
        

def composeClassifiers(categories: list, train_size: float) -> dict:
    """ Generate classifier package

    For each category an individual classifier will be provided. This function covers pipeline generation, optimization, training, and zipping.

    Args:
        categories (list): the learning items, per element a separate classifier will be trained
        train_size (float): tuning parameter: train_size of sklearn's `train_test_split`

    Returns:
        dict: the prepared classifiers
    """
    
    estimators = dict()
    
    # make a pipeline per category
    for category in categories:
        X_train, X_test, y_train, y_test = train_test_split(X, Y[category], train_size=train_size)

        pipeline = Pipeline([
                ('vect', CountVectorizer(tokenizer=tokenize)),
                ('tfidf', TfidfTransformer()),
                ('clf', RandomForestClassifier())
            ])
        parameters = {
                'features__text_pipeline__vect__ngram_range': ((1, 1), (1, 2)),
                'clf__n_estimators': [10, 20, 25, 50, 100, 200],
                'clf__min_samples_split': [2, 3, 4]
            }

        # optimize
        cv = GridSearchCV(pipeline, param_grid=parameters)
        # train
        pipeline.fit(X_train, y_train)
        # push back
        estimators.update({category: {"clf": pipeline, "test_data": {"X": X_test, "y": y_test}, "train_data": X_train}})

    return estimators


def exportClassifier(
    estimators: dict, 
    learnedCategories: list,
    outputPath: str = os.path.join(os.path.dirname(os.path.realpath(__file__)),  "..", "ressources", "classifier.pkl")):
    """ Store the classifiers persistently

    Args:
        estimators (dict): the struct to be stored
        learnedCategories (list): the list of categories the estimators work on
        outputPath (str, optional): Where the file should be written to.
    """
    with open(outputPath, "wb") as clfFile:
        # compose ...
        exportPackage = dict()  # focus on the classifiers alone
        for key in estimators.keys():
            exportPackage.update({key: estimators[key]["clf"]})
            exportPackage.update({"messages": estimators[key]["train_data"]})
        exportPackage.update({"learned_categories": learnedCategories})

        # ... and store
        pickle.dump(exportPackage, clfFile)
    print(f"Successfully exported package to '{outputPath}'")


def runPerformanceAnalysis(estimators: dict):
    """ Walks through the estimators and prints their performance

    Args:
        estimators (dict)
    """

    for category in estimators.keys():
        print(f"Evaluating {category}")
        estimator = estimators[category]
        testModel(estimator["test_data"]["X"], estimator["test_data"]["y"], estimator["clf"])
        print("---\n")
    

def tokenize(text: str) -> list:
    """ Turns a message string into separate word elements

    Args:
        text (str): the message string to process

    Returns:
        clean_tokens (list): the separate world elements
    """
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)

    return clean_tokens


def testModel(X_test: list, y_test: list, pipeline):
    """ Evaluates a classifier performance

    Prints the results in the console

    Args:
        X_test: test samples
        y_test: ground truth
        pipeline: the classifier to be evaluated
    """
    y_pred = pipeline.predict(X_test)
    confusion_mat = confusion_matrix(y_test, y_pred)
    accuracy = (y_pred == y_test).mean()

    print("Confusion Matrix:\n", confusion_mat)
    print("Accuracy:", accuracy)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-ts", "--train-size", default=0.99)
    args = parser.parse_args()
    
    df = loadDataset()
    X = df["message"]
    Y = dict()

    groundTruth = df.drop(["message", "id", "original", "genre", "related"], axis=1)
    categories = groundTruth.columns
    for category in categories:
        Y.update({category: groundTruth[category]})

    estimators = composeClassifiers(categories, float(args.train_size))

    exportClassifier(estimators, groundTruth.columns)
    
    doAnalyis = True
    if doAnalyis:
        runPerformanceAnalysis(estimators)



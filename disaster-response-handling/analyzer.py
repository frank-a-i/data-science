from pipelines.ml import tokenize

import os
import sys
import pickle
import random

class QueryAnalyzer:
    def __init__(self, classifierPath=os.path.join(os.path.dirname(os.path.realpath(__file__)), "ressources", "classifier.pkl")):
        """
        Args:
            classifierPath (_type_, optional): from where the trained classifiers should be loaded
        """
        self._classifierPath = classifierPath
        self._ensembleClf = None
        self._messages = None

    def load(self):
        """ Load persistently stored, trained classifiers and gets ready for usage """
        with open(self._classifierPath, "rb") as clfFile:
            self._ensembleClf = pickle.load(clfFile)
            self._messages = self._ensembleClf["messages"].tolist()
            del self._ensembleClf["messages"]
            del self._ensembleClf["learned_categories"]
        print("Classifier loaded")

    def demoMessage(self) -> str:
        """ Draw arbitrary demo message

        Returns:
            str: demo message
        """
        return random.choice(self._messages)

    def analyse(self, query: str):
        """ Evaluate message

        Args:
            query (str): the message to be evaluated

        Returns:
            str: a summary of probabilities per category
        """
        
        result_str = ""
        for category in self._ensembleClf.keys():
            prediction = self._ensembleClf[category].predict_proba([query])
            result_str = f"{result_str} {category}:{prediction},"

        return result_str

if __name__ == "__main__":
    demoAnalyzer = QueryAnalyzer()
    demoAnalyzer.load()
    query = str(sys.argv[1])
    print(f"Analyzing {query}")
    print(demoAnalyzer.analyse(query))
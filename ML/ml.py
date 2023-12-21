
import pandas as pd
import numpy as np
from sqlalchemy.engine import create_engine
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV

from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
import os
nltk.download(['punkt', 'wordnet'])

df = pd.read_sql_table('TableFAI', f'sqlite:///{os.path.join(os.path.dirname(os.path.realpath(__file__)),  "..", "ressources", "ETLFAI.db")}')
learning_item = "aid_related"
df_clean = df.drop(df[np.isnan(df[learning_item])].index)
df_clean.dropna(inplace=True)
X = df_clean["message"]
Y = dict()

groundTruth = df_clean.drop(["message", "id", "original", "genre"], axis=1)
categories = groundTruth.columns
for category in categories:
    Y.update({category: groundTruth[category]})

def tokenize(text):
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)

    return clean_tokens



def test_model(X_test, y_test, pipeline):
    y_pred = pipeline.predict(X_test)
    confusion_mat = confusion_matrix(y_test, y_pred)
    accuracy = (y_pred == y_test).mean()

    print("Confusion Matrix:\n", confusion_mat)
    print("Accuracy:", accuracy)

estimators = dict()

for category in categories:
    X_train, X_test, y_train, y_test = train_test_split(X, Y[category])

    #train_model()

    #test_model()


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


    cv = GridSearchCV(pipeline, param_grid=parameters)
    pipeline.fit(X_train, y_train)
    
    estimators.update({category: {"clf": pipeline, "test_data": {"X": X_test, "y": y_test}}})

for category in categories:
    print(f"Evaluating {category}")
    estimator = estimators[category]
    test_model(estimator["test_data"]["X"], estimator["test_data"]["y"], estimator["clf"])
    print("---\n")
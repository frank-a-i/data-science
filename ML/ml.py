
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
Y = df_clean[learning_item]


def tokenize(text):
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)

    return clean_tokens


pipeline = Pipeline([
        ('vect', CountVectorizer(tokenizer=tokenize)),
        ('tfidf', TfidfTransformer()),
        ('clf', RandomForestClassifier())
    ])

X_train, X_test, y_train, y_test = train_test_split(X, Y)

def train_model():
    pipeline.fit(X_train, y_train)
train_model()

def test_model():
    y_pred = pipeline.predict(X_test)
    confusion_mat = confusion_matrix(y_test, y_pred)
    accuracy = (y_pred == y_test).mean()

    print("Confusion Matrix:\n", confusion_mat)
    print("Accuracy:", accuracy)
test_model()


parameters =  parameters = {
        'features__text_pipeline__vect__ngram_range': ((1, 1), (1, 2)),
        'clf__n_estimators': [10, 20, 25, 50, 100, 200],
        'clf__min_samples_split': [2, 3, 4]
    }


cv = GridSearchCV(pipeline, param_grid=parameters)
train_model()
test_model()
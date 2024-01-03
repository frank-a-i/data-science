from flask import Flask

from pipelines.ml import tokenize
app = Flask(__name__)

from UI import routes
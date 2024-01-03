from UI import app
from flask import render_template, url_for, request, send_from_directory
from analyzer import QueryAnalyzer
import pickle
import os

defaultAnalyzer = QueryAnalyzer()

def getAppConfig(classifierPath: str = os.path.join(os.path.dirname(os.path.realpath(__file__)),  "..", "ressources", "classifier.pkl")):
    """ Returns categories to evaluate and layout property

    Args:
        classifierPath (str, optional): where the classifier has been exported to.

    Returns:
        int: ideal number of visuals per row, list: categories
    """
    # load data
    with open(classifierPath, "rb") as pickleFile:
        classifierPackage = pickle.load(pickleFile)
    categories = [cat.replace("_", " ") for cat in classifierPackage["learned_categories"]]
    
    # identify best fit for number of visuals per row
    numElementsPerRow = 1
    for curNumElementsPerRow in range(5, 20):
        if len(categories) % curNumElementsPerRow == 0:
            numElementsPerRow = curNumElementsPerRow
            break

    return numElementsPerRow, categories


# web pages
@app.route('/')
@app.route('/index')
def index():
    return render_template('loading.html')

@app.route('/analyser', methods=["GET", "POST"])
def run_app(summaryDescr="Inspection"):
    numElementsPerRow, categories = getAppConfig()
    return render_template('index.html', summaryDescr=summaryDescr, numElementsPerRow=numElementsPerRow, numCategories=len(categories), categories=categories)

# callbacks
@app.route('/loading', methods=["POST"])
def load_application():

    defaultAnalyzer.load()
    return "N/A"

@app.route('/runAnalytics', methods=['POST'])
def run_analytics():
    return defaultAnalyzer.analyse(request.form["param"])

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.route("/demo", methods=['POST'])
def getDemoMessage():
    return defaultAnalyzer.demoMessage()
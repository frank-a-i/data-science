from UI import app
from flask import render_template#, url_for, request, send_from_directory


# web pages
@app.route('/')
@app.route('/recommendation')
def recommendations():
    return render_template('recommendation.html')

@app.route('/insights')
def insights():
    return render_template('insights.html')

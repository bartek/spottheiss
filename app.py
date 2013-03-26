import os
from flask import Flask, render_template, jsonify, request
from heavens_above import heavens_to_object, get_timezone

app = Flask(__name__)
app.debug = True

CONFIG = os.environ.get('CONFIG', None)
if not CONFIG:
    CONFIG = 'config'
app.config.from_object(CONFIG)

@app.route("/iss")
def fetch_iss():
    lat = request.args.get('lat')
    lng = request.args.get('lng')

    tz = get_timezone(app.config['ASKGEO'], lat, lng)
    data = heavens_to_object(25544, lat, lng, tz['ShortName'])
    return jsonify(passes=data)

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()

import json
import copy
import requests
from HTMLParser import HTMLParser

heavens_url = "http://heavens-above.com/PassSummary.aspx"

class SuperSpaceParser(HTMLParser):
    columns = (
        'date',
        'brightness',
        'start_time',
        'start_alt',
        'start_az',
        'highest_time',
        'highest_alt',
        'highest_az',
        'end_time',
        'end_alt',
        'end_az',
        'pass_time',
    )

    def __init__(self):
        self.reset()

        # Container for each pass we find.
        self.passes = []
        self.is_data_row = False
        self.current_pass = {}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'tr' and attrs_dict.get('class', '').startswith('clickableRow'):
            self.is_data_row = True

    def handle_data(self, data):
        if self.is_data_row:
            index = len(self.current_pass.keys())
            self.current_pass[self.columns[index]] = data

    def handle_endtag(self, tag):
        # Close the row once we've hit the ending tr
        if self.is_data_row and tag == 'tr':
            self.is_data_row = False
            self.passes.append(copy.deepcopy(self.current_pass))
            self.current_pass = {}

def get_timezone(conf, lat, lng):
    # askgeo api helper.
    params = {
        'databases': 'TimeZone',
        'points': '%s,%s' % (lat, lng),
    }
    req = requests.get(
        "http://api.askgeo.com/v1/{0}/{1}/query.json"
            .format(conf['userid'], conf['application_key']), params=params)

    if req.status_code == requests.codes.ok:
        tz = json.loads(req.content)['data'][0]['TimeZone']

        # Translate to not break heavens-above
        if tz['ShortName'] == 'EDT':
            tz['ShortName'] = 'EST'

        return tz
    req.raise_for_status()

def heavens_to_object(satid, lat, lng, tz):
    """
    Scrape heavens-above url, converting the data found to 
    a list of dicts.
    """
    params = {
        'satid': satid,
        'lat': lat,
        'lng': lng,
        'tz': tz,
    }
    req = requests.get(heavens_url, params=params)

    parser = SuperSpaceParser()

    if req.status_code == requests.codes.ok:
        parser.feed(req.content)
        return parser.passes
    req.raise_for_status()

if __name__ == "__main__":
    # Toronto!
    data = heavens_to_object(25544, 41.8500, -87.6500, "EST")

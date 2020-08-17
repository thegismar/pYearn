from chainclient import ChainClient
import flask
from flask import jsonify

app = flask.Flask(__name__)

cc = ChainClient()
roi = []

for address in cc.contract_address:
    d = {'vault': address, 'hourly': f'{cc.get_roi_hour(address):.5%}', 'daily': f'{cc.get_roi_day(address):.5%}',
         'weekly': f'{cc.get_roi_week(address):.5%}', 'yearly': f'{cc.get_roi_year(address):.5%}'}


@app.route('/api/', methods=['GET'])
def api_all():
    return jsonify(d)


app.run()

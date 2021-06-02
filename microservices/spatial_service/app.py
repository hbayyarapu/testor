from flask import Flask

import os

client_name = os.environ['client']

app = Flask(__name__)

@app.route('/')
def index():
    return f'Spatial Service - {client_name} - This is version 0.1.0'

@app.route('/service')
def service():
    return {'value': 100 }

app.run(host='0.0.0.0', port=81)

from flask import Flask

import os

client_name = os.environ['client']
s3_bucket = os.environ['s3_bucket']

app = Flask(__name__)

@app.route('/')
def index():
    return f'Spatial Service - {client_name} - {s3_bucket} This is version 0.2.1'

@app.route('/service')
def service():
    return {'weight': 100 , 'client': client_name}

app.run(host='0.0.0.0', port=81)

import json
import importlib
import os
from traceback import format_exc

import pandas as pd
from flask import Flask, request
from werkzeug.exceptions import InternalServerError

app = Flask(__name__)


@app.errorhandler(InternalServerError)
def internal_server_error_handler(error):
    response = {
        'message': InternalServerError.description,
        'exception': repr(error),
        'traceback': format_exc(),
    }
    return json.dumps(response), 500


def get_url_prefix():
    return os.environ.get('URL_PREFIX', '')


def get_custom_model_instance():
    module_name = os.environ.get('MODULE_NAME')
    class_name = os.environ.get('CLASS_NAME')
    custom_model_module = importlib.import_module(module_name)
    CustomModelClass = getattr(custom_model_module, class_name)
    return CustomModelClass()


custom_model = get_custom_model_instance()
url_prefix = get_url_prefix()


@app.route('{}/predict/'.format(url_prefix), methods=['POST'])
def predict():
    payload = request.form
    X = pd.read_csv(request.files['X'])
    predictions = custom_model.predict(X)
    return json.dumps({'predictions': [pred for pred in predictions]})


@app.route('{}/'.format(url_prefix))
def ping():
    """This route is used to ensure that server has started"""
    return 'Server is up!\n'

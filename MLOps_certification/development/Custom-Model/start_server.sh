#!/bin/sh
cd /opt/code/ || exit 1
export PYTHONPATH=/opt/code
export FLASK_APP=server.app
export MODULE_NAME=inference_model_scoring
export CLASS_NAME=CustomInferenceModel
python -m flask run --host=0.0.0.0 --port 8080

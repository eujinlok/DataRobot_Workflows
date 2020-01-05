"""
@author: Eu Jin Lok

Send a new data to the deployed model to get predictions 


NOTE: 
- Items to bring to new environment 
    - requirement.txt                
    - config.yaml  
    - New results.json -- obtained from running '2. Model Deployment.py' script 
    - <this script>.py
- Python environment was used but not commited to repo. Initiate python environment on the terminal:
    python3 -m venv API_Workflow_EndtoEnd/new_env
    source API_Workflow_EndtoEnd/new_env/bin/activate
- Intall required libraries:
    pip install -r API_Workflow_EndtoEnd/requirements.txt 
- .yaml file not commited. Use your own API token and other credentials 
"""

######################################
# %% Import libraries and set the config path 
import sys, os
import pandas as pd
import datarobot as dr
from datarobot import Project, Deployment
import pickle
import requests
import json
import time 
print(sys.version)
dr.Client(config_path=os.getcwd()+'/API_Workflow_EndtoEnd/config.yaml')

# %% Retrieve to correct model ID and Project ID - the one that was deployed 
# ie delays2013_prod_similar
with open('API_Workflow_EndtoEnd/New_result.json') as f:
    param = json.load(f)

project = dr.Project.get(param['project ID'])
model = dr.Model.get(project=param['project ID'],
                     model_id=param['Model ID'])

# Using path to local file to generate predictions
test = project.upload_dataset(os.getcwd() + "/retrain_python/logan-US-2014.csv")
predict_job_1 = model.request_predictions(test.id)

# wait for a while... 
time.sleep(10)

# Submit prediction into the queue
predict_job = dr.PredictJob.get(project_id=param['project ID'],
                                predict_job_id = predict_job_1.id)

# now the predictions are finished
predictions = dr.PredictJob.get_predictions(project_id=project.id,
                                            predict_job_id=predict_job_1.id)

predictions.head()


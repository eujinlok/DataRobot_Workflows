"""
@author: Eu Jin Lok

Setup datadrift on deployment and feedback accuracy for tracking. This script will initialise a data drift tracker 
and feedback actuals to datarobot. Full documentation: 
https://datarobot-public-api-client.readthedocs-hosted.com/en/v2.18.0/entities/deployment.html#create-a-deployment


NOTE: 
- Items to bring to new environment 
    - requirement.txt                
    - config.yaml  
    - <this script>.py
- Python environment was used but not commited to repo. Initiate python environment on the terminal:
    python3 -m venv API_Workflow_EndtoEnd/new_env
    source API_Workflow_EndtoEnd/new_env/bin/activate
- Intall required libraries:
    pip install -r API_Workflow_EndtoEnd/requirements.txt 
- .yaml file not commited. Use your own API token and other credentials 
"""

# %% #########################################
# Import libraries and set the config path 
import sys, os
import pandas as pd
import numpy as np
import datarobot as dr
from datarobot import Project, Deployment
from datarobot.enums import SERVICE_STAT_METRIC, ACCURACY_METRIC
import pickle
import requests
import json
import time 
from datetime import datetime
import matplotlib
print(sys.version)
dr.Client(config_path=os.getcwd()+'/API_Workflow_EndtoEnd/config.yaml')

# Custom fuction required for tracking data drift 
def set_association_id(deployment_id, association_id, allow_missing_values=False):
    """Assigns the association ID for a deployment"""
    url = f'{BASE_URL}/modelDeployments/{deployment_id}/associationIdSettings/'
    
    data = {'allowMissingValues': allow_missing_values, 'columnName': association_id}
    
    resp = requests.patch(url, json=data, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

# %% #########################################
# START 
with open('API_Workflow_EndtoEnd/Deployment_Creds.json') as f:
    param = json.load(f)

DATAROBOT_KEY = param['DATAROBOT_KEY']
API_KEY = param['API_KEY']
USERNAME = param['USERNAME']
DEPLOYMENT_ID = '5dbe5e49397e660046399f92'
MAX_PREDICTION_FILE_SIZE_BYTES = 52428800  # 50 MB

deployment = dr.Deployment.get(deployment_id=DEPLOYMENT_ID)


# %%
# Activate data drift 
# deployment.update_drift_tracking_settings(target_drift_enabled=True, feature_drift_enabled=True)

# now check that it has been set
deployment.get_drift_tracking_settings()

# Get service stats 
# need to make sure there's some predictions submited in the last 7 days or it will error
deployment.get_service_stats()

# Total number of predictions stat
service_stats[SERVICE_STAT_METRIC.TOTAL_PREDICTIONS]


# %% #####################################
# Setup process to feedback actuals 
# Assign an association ID to the deployment and set up drift tracking
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization':  f'Token {API_KEY}'
}

association_id_column_name = 'event_id'
BASE_URL = 'https://app.datarobot.com/api/v2'

set_association_id(deployment.id, association_id_column_name, allow_missing_values=False)

# %%
# Feedback actuals - Lets modify the test data to include the Event ID column 
df = pd.read_csv("retrain_python/logan-US-2014.csv")
df["event_id"] = df.index + int(datetime.now().strftime('%Y%m%d%H%M'))*100000

# Randomise a few columns to get some changes 
df = df.sample(n=25000, random_state=42, replace = True)

# Lets generate a simulated dataset for submission and run the 
# Model_Monitoring_Management.py script 
df['daily_rainfall'] = np.random.random_integers(0,10,len(df)) /1000
df.to_csv("retrain_python/logan-US-2014_event_id.csv", index = False)

# %% 
# Now feedback actuals 
# NOTE: Make sure you run:
# python API_Workflow_EndtoEnd/Model_Monitoring_Management.py "retrain_python/logan-US-2014_event_id.csv"
df = pd.read_csv("retrain_python/logan-US-2014_event_id.csv")
df = df[['event_id','was_delayed']]
df.event_id = df.event_id.astype(str)
df.was_delayed = df.was_delayed.astype(str)
df['was_acted_on'] = 'True'
df.columns = ['association_id','actual_value','was_acted_on']
deployment.submit_actuals(df[0:10000])  # For a large dataset do - df = df.to_dict(orient='records')
deployment.submit_actuals(df[10001:20000])  # For a large dataset do - df = df.to_dict(orient='records')
deployment.submit_actuals(df[20001:25000])  # For a large dataset do - df = df.to_dict(orient='records')


# Now lets check how much the accuracy has drifted
accuracy = deployment.get_accuracy()
accuracy[ACCURACY_METRIC.AUC]

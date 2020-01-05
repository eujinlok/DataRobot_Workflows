"""
@author: Eu Jin Lok

Deploying model onto a new environment to enable predictions, using the serialised model

NOTE: 
- Items to bring to new environment 
    - requirement.txt                
    - <training data>.csv
    - bk.pkl
    - config.yaml  
    - results.json -- optional 
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
print(sys.version)
dr.Client(config_path=os.getcwd()+'/API_Workflow_EndtoEnd/config.yaml')

# %% Project Creation 
df = pd.read_csv(
    os.getcwd() + "/retrain_python/logan-US-2013.csv"
)
df.head()

project = dr.Project.create(df, project_name = 'delays2013_prod_similar')
featurelist = project.create_featurelist('myfeatures', list(df.columns.values))

# %% Manual model settings
# run manual mode to pick up that same blueprint (don't want to have a different blueprint between DEV and PROD)
project.set_target(target='was_delayed'
    , featurelist_id = featurelist.id
    , metric = 'AUC'
    , mode = dr.AUTOPILOT_MODE.MANUAL
    , worker_count= -1 
    )

# now get the blueprint that we pickled from script '1. Model Training.py'
old_bp = pickle.load(open('API_Workflow_EndtoEnd/bp.pkl', 'rb'))

# Get a blueprint that is of the same type, with the same feature engineering 
new_bp = [bp for bp in project.get_blueprints() if old_bp.processes == bp.processes][0]
print(new_bp)

# train this bluerpint on 80% 
job = project.train(new_bp
    , sample_pct=80 
    , source_project_id= project.id)

model =dr.models.modeljob.wait_for_async_model_creation(project.id, job)

# %% Create a deployment 
pred_server = dr.PredictionServer.list()[0].id 

deployment = Deployment.create_from_learning_model(
    model.id
    , 'Deployment Test'
    , default_prediction_server_id=pred_server
    )

# Because this is the model / project that we are using going forward, 
# we need to store its artificates in replacement of the original 
# ie. project 'delays2013' is now old. We use 'delays2013_prod_similar'
param = {
    "project ID": project.id,
    "Model Name": str(model),
    "Model ID": model.id,
    "Model Blueprint ID": model.blueprint_id,
    "Model Blueprint Process": str(model.processes)
}

with open('API_Workflow_EndtoEnd/New_result.json', 'w') as fp:
    json.dump(param, fp)





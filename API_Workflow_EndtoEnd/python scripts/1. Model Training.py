"""
@author: Eu Jin Lok

Using the API to train a model on DataRobot, and serialise the model  

NOTE: 
- Python environment was used but not commited to repo. Initiate python environment on the terminal:
    python3 -m venv API_Workflow_EndtoEnd/new_env
    source API_Workflow_EndtoEnd/new_env/bin/activate
- Intall required libraries:
    pip install -r API_Workflow_EndtoEnd/requirements.txt 
- .yaml file not commited. Use your own API token and other credentials 
"""

# %% Import libraries and set the config path 
import sys, os
import pandas as pd
import datarobot as dr
from datarobot import Project, Deployment
import pickle
import requests
import json
print(sys.version)
dr.Client(config_path=os.getcwd()+'/API_Workflow_EndtoEnd/config.yaml')

# %% Project Creation 
df = pd.read_csv(
    os.getcwd() + "/retrain_python/logan-US-2013.csv"
)
df.head()

# create a project in Datarobot now, can also be a filepath directory to a url
project = dr.Project.create(df, project_name = 'delays2013')  # set wait time for large datasets - max_wait=2000, read_timeout=2000

# %% Setup autopilot 
# Check on DataRobot app that the data is uploaded, project called 'delays2013'
# now we run autopilot 
project.get_metrics('was_delayed')['available_metrics']

# to get reduced features
featurelist = project.create_featurelist('myfeatures', list(df.columns.values))

# run autopilot
project.set_target(target = 'was_delayed'
    , featurelist_id = featurelist.id
    , metric ='AUC'
    , mode = dr.AUTOPILOT_MODE.FULL_AUTO
    , worker_count = -1
    )
project.wait_for_autopilot()

# %% Serealise ##
# Use DataRobot's recommended model that is NOT a blender 
#################
best_model = dr.ModelRecommendation.get(project.id).get_model()
print(best_model)
best_model.blueprint_id

# serialize this and store somewhere
bp = [bp for bp in project.get_blueprints() if bp.id == best_bp][0]
pickle.dump(bp, open('bp.pkl', 'wb'))

# store the artifacts for future references 
param = {
    "project ID": project.id,
    "Model Name": str(best_model),
    "Model ID": best_model.id,
    "Model Blueprint ID": best_model.blueprint_id,
    "Model Blueprint Process": str(best_model.processes)
}

with open('API_Workflow_EndtoEnd/result.json', 'w') as fp:
    json.dump(param, fp)


 



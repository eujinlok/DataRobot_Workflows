"""
@author: Eu Jin Lok

Using the API to train a specific model on the entire data set

NOTE: 
- Python environment was used but not commited to repo. Initiate python environment on the terminal:
    python3 -m venv API_Workflow_EndtoEnd/new_env
    source API_Workflow_EndtoEnd/new_env/bin/activate
- Intall required libraries:
    pip install -r API_Workflow_EndtoEnd/requirements.txt 
- .yaml file not commited. Use your own API token and other credentials 
"""

# %% Import Libraries 
# Import libraries and set the config path 
import sys, os
import pandas as pd
import datarobot as dr
from datarobot import Project, Deployment
import pickle
import requests
import json
print(sys.version)
dr.Client(config_path=os.getcwd()+'/API_Workflow_EndtoEnd/config.yaml')

# %% Find ID
# List out the various projects, its name and its ID
dr.Project.list()
All_p = dr.Project.list()
ids = [p.id for p in All_p]

'''
# Create an empty dataframe object 
df = pd.DataFrame({'project name': [], 'id': []})

# loop through the list and append both name and ID to the empty dataframe
for p in All_p:
    df = df.append(
        {'project name': p.project_name
        ,'id': p.id 
        },ignore_index = True
    )
'''

# %% Retrain 
# Get the first Project ID, and the correct model ID
project = dr.Project.get(ids[0])
models = project.get_models()

# Unlock the holdout and get the model 
project.unlock_holdout()
model = dr.Model.get(project=ids[0],
                     model_id=models[0].id)

# Train on 100% of the data 
model100 = model.train(sample_pct=100)


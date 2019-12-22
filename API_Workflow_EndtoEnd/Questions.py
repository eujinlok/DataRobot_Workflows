"""
@author: Eu Jin Lok

Answering some adhoc questions 

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
dr.__version__

# %% Question 1 
# Is DR reduced features such as 'DR Reduced Features M63' kept in BluePrints?
# Answer - NO
All_p = dr.Project.list()
ids = [p.id for p in All_p]

# Get one project as example 
id = '5de091903e49ca13f2954e6e'
project = dr.Project.get(id)

all_m = project.get_models()
theone = all_m[7] # get the model version that has a reduced feature list used. 

best_bp = theone.blueprint_id
bp = [bp for bp in project.get_blueprints() if bp.id == best_bp][0]
bp.processes   # the feature list not stored 

# To get access to the Reduced feature list 
project.get_modeling_featurelists()
feat2. = project.get_modeling_featurelists()[3] 
feat2.features 
# This will have to be saved into the blueprint pickle file.  




# Getting access to the objects / methods inside an object class 
old_bp = pickle.load(open('API_Workflow_EndtoEnd/bp.pkl', 'rb'))
dir(old_bp)



# John Edwards alternative method of the BluePrint 

build_bp_data = {
    'blueprint': 'Blueprint(eXtreme Gradient Boosted Trees Classifier with Early Stopping (learning rate =0.01))',
    'type': 'eXtreme Gradient Boosted Trees Classifier with Early Stopping (learning rate =0.01)',
    'processes': ['One-Hot Encoding',
    'Univariate credibility estimates with ElasticNet',
    'Converter for Text Mining',
    'Auto-Tuned Word N-Gram Text Modeler using token occurrences',
    'Missing Values Imputed',
    'Search for differences',
    'Search for ratios',
    'eXtreme Gradient Boosted Trees Classifier with Early Stopping (learning rate =0.01)'],
    'features': ['a1cresult',
    'acarbose',
    'acetohexamide',
    'admission_source_id',
    'weight']
    }


from collections import namedtuple
if 'blueprint' in build_bp_data.keys():
    build_bp_data.pop('blueprint')

build_bp = namedtuple('Struct', build_bp_data.keys())(*build_bp_data.values())
print(build_bp)








# John Edward's code for JQ 

def deploy_model():
    """
    This method deploys the best model blue print.
    """
    ################################################################################
    # run top blueprint in a new project
    # note for a new environment, you'd want a new config pointing to the install
    # could be a dr.Client
    creds = get_temp_credentials(role)
    access_key_id = creds["Credentials"]["AccessKeyId"]
    secret_access_key = creds["Credentials"]["SecretAccessKey"]
    session_token = creds["Credentials"]["SessionToken"]
    print("Deploying to {}".format(environment))
    try:
        aws.S3().download_file('jq-ada-artefact-storage', '/tmp/bp.pkl', 'jq-ada/datarobot/' +
                               model_project_name + '-bp.pkl')
    except RuntimeError:
        print("Model does not exist")
        quit()
    print("Source type:         ", deployment_source_type)
    print("Source location/key: ", deployment_source_location)
    print("Source filename:     ", deployment_source_filename)
    print("Source bucket:       ", deployment_source_bucket)
    print("Datarobot Host:      ", datarobot_host)
    df = get_datasource(deployment_source_type, deployment_source_filename, deployment_source_bucket,
                        deployment_source_location, deployment_source_encoding, access_key_id, secret_access_key, session_token)
    deployment_id = get_deployments(deployment_label)
    # make the same project, with the same settings
    project = dr.Project.create(df, project_name=deployment_project_name,
                                read_timeout=2000, max_wait=2000,)
    featurelist = project.create_featurelist('myfeatures', list(df.columns.values))
    # run in manual model
    project.set_target(target=model_target, featurelist_id=featurelist.id,
                       metric=model_target_metric, mode=dr.AUTOPILOT_MODE.MANUAL,
                       worker_count=4, max_wait=2000,)
    # read original blueprint
    old_bp = pickle.load(open('/tmp/bp.pkl', 'rb'))
    print("read the pkl file {}".format(old_bp))
    # get a blueprint that is of the same type, but could have different feature engineering
    # new_bp = [bp for bp in project.get_blueprints() if old_bp.model_type == bp.model_type][0]
    # get a blueprint of the same type and with the same feature engineering
    # new_bp = [bp for bp in project.get_blueprints() if old_bp.processes == bp.processes][0]
    # train this blueprint on 80%
    job = project.train(old_bp, sample_pct=80, source_project_id=project.id)
    model = dr.models.modeljob.wait_for_async_model_creation(project.id, job, max_wait=72000)
    # optionally set prediction threshold for binary classification
    # check_roc = None
    #
    # try:
    #     model.get_roc_curve('crossValidation')
    # except dr.errors.ClientError:
    #     check_roc = False
    #
    # if check_roc:
    #     roc = model.get_roc_curve('crossValidation')
    #     threshold = roc.get_best_f1_threshold()
    #     model.set_prediction_threshold(threshold)
    ################################################################################
    # create a deployment or update if one alreadt exists
    if deployment_id:
        print("Updating deployment...")
        request_body = {
            'modelId': model.id,
            'reason': "Data Drift"
        }
        response = web.Http().call_api(datarobot_host, "patch", "/api/v2/modelDeployments/"
                                       + deployment_id + "/model/", environment, request_body)
        print(response)
    else:
        request_body = {
            # link to model using project and model ids
            'projectId': project.id,
            'modelId': model.id,
            # name and description of deployment
            'label': deployment_label,
            'description': deployment_description,
            'deploymentType': 'dedicated'
        }
        response = web.Http().call_api(datarobot_host, "post",
                                       "/api/v2/modelDeployments/asyncCreate/", environment, request_body)
        print("deployment_id: ", response["id"])
    
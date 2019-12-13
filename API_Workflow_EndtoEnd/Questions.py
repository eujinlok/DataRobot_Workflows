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


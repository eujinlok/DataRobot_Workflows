# pylint: disable-all
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import make_column_transformer
from sklearn.feature_extraction.text import TfidfVectorizer

import pickle
import pandas as pd
import numpy as np

PATH_TO_DATAFRAME = (
    'https://s3.amazonaws.com/datarobot_public_datasets/10k_diabetes_no_null_text.csv'
)

# Train/test split
df = pd.read_csv(PATH_TO_DATAFRAME)
y = df.pop('readmitted')
X_train, X_test, y_train, y_test = train_test_split(df, y)

numeric_features = list(X_train.select_dtypes(include=np.number).columns.values)
text_features = ['diag_1_desc', 'diag_2_desc', 'diag_3_desc']
categorical_features = list(set(X_train.columns) - set(numeric_features + text_features))


# Set up preprocessing steps for each type of feature
text_preprocessing = Pipeline([('TfIdf', TfidfVectorizer())])

categorical_preprocessing = Pipeline(
    [
        ('Imputation', SimpleImputer(strategy='constant', fill_value='?')),
        ('One Hot Encoding', OneHotEncoder(handle_unknown='ignore')),
    ]
)

numeric_preprocessing = Pipeline(
    [('Imputation', SimpleImputer(strategy='mean')), ('Scaling', StandardScaler())]
)


preprocessing = make_column_transformer(
    (numeric_features, numeric_preprocessing),
    (text_features[0], text_preprocessing),
    (text_features[1], text_preprocessing),
    (text_features[2], text_preprocessing),
    (categorical_features, categorical_preprocessing),
)

pipeline = Pipeline(
    [('Preprocessing', preprocessing), ('Logistic Regression', LogisticRegression())]
)

pipeline.fit(X_train, y_train)

with open('custom_model.pickle', 'wb') as picklefile:
    pickle.dump(pipeline, picklefile)

"""
Usage:
    python datarobot-predict.py <input-file.csv>

This example uses the requests library which you can install with:
    pip install requests
We highly recommend that you update SSL certificates with:
    pip install -U urllib3[secure] certifi
"""
import sys
import requests

DATAROBOT_KEY = '544ec55f-61bf-f6ee-0caf-15c7f919a45d'
API_KEY = 'NWQ4MGQyYjJhNTdhY2QwYzRjMTZkOTcxOlNwVi8vcWN6Qm1uK0ZpK29ZYVZmSzhBWHZnNU00Ulp1MEtsSTZRTkFjMDg9'
USERNAME = 'eu.jin.lok@datarobot.com'

DEPLOYMENT_ID = '5e003cc8dd923b0579cc93c4'
MAX_PREDICTION_FILE_SIZE_BYTES = 52428800  # 50 MB


class DataRobotPredictionError(Exception):
    """Raised if there are issues getting predictions from DataRobot"""


def make_datarobot_deployment_predictions(data, deployment_id):
    """
    Make predictions on data provided using DataRobot deployment_id provided.
    See docs for details:
         https://app.datarobot.com/docs/users-guide/predictions/api/new-prediction-api.html

    Parameters
    ----------
    data : str
        Feature1,Feature2
        numeric_value,string
    deployment_id : str
        The ID of the deployment to make predictions with.

    Returns
    -------
    Response schema:
        https://app.datarobot.com/docs/users-guide/predictions/api/new-prediction-api.html#response-schema

    Raises
    ------
    DataRobotPredictionError if there are issues getting predictions from DataRobot
    """
    # Set HTTP headers. The charset should match the contents of the file.
    headers = {'Content-Type': 'text/plain; charset=UTF-8', 'datarobot-key': DATAROBOT_KEY}

    url = 'https://cfds-ccm-prod.orm.datarobot.com/predApi/v1.0/deployments/{deployment_id}/'\
          'predictions'.format(deployment_id=deployment_id)
    # Make API request for predictions
    predictions_response = requests.post(
        url,
        auth=(USERNAME, API_KEY),
        data=data,
        headers=headers,
    )
    _raise_dataroboterror_for_status(predictions_response)
    # Return a Python dict following the schema in the documentation
    return predictions_response.json()


def _raise_dataroboterror_for_status(response):
    """Raise DataRobotPredictionError if the request fails along with the response returned"""
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        err_msg = '{code} Error: {msg}'.format(
            code=response.status_code, msg=response.text)
        raise DataRobotPredictionError(err_msg)


def main(filename, deployment_id):
    """
    Return an exit code on script completion or error. Codes > 0 are errors to the shell.
    Also useful as a usage demonstration of
    `make_datarobot_deployment_predictions(data, deployment_id)`
    """
    if not filename:
        print(
            'Input file is required argument. '
            'Usage: python datarobot-predict.py <input-file.csv>')
        return 1
    data = open(filename, 'rb').read()
    data_size = sys.getsizeof(data)
    if data_size >= MAX_PREDICTION_FILE_SIZE_BYTES:
        print(
            'Input file is too large: {} bytes. '
            'Max allowed size is: {} bytes.'
        ).format(data_size, MAX_PREDICTION_FILE_SIZE_BYTES)
        return 1
    try:
        predictions = make_datarobot_deployment_predictions(data, deployment_id)
    except DataRobotPredictionError as exc:
        print(exc)
        return 1
    print(predictions)
    return 0


if __name__ == "__main__":
    filename = sys.argv[1]
    sys.exit(main(filename, DEPLOYMENT_ID))

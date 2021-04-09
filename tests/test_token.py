"""
Unit tests to test formatting.
"""

import logging
from os import getenv
from os.path import join, dirname

from dotenv import load_dotenv #pylint: disable=import-error
from scalesec_gcp_workload_identity.main import TokenService #pylint: disable=import-error

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('gcp_token_federation').setLevel(logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# load values from env
dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path=dotenv_path)

# init the token service
token_service = TokenService(
    gcp_project_number=getenv('GCP_PROJECT_NUMBER'),
    gcp_workload_id=getenv('GCP_WORKLOAD_ID'),
    gcp_workload_provider=getenv("GCP_WORKLOAD_PROVIDER"),
    gcp_service_account_email=getenv('GCP_SERVICE_ACCOUNT_EMAIL'),
    aws_account_id=getenv('AWS_ACCOUNT_ID'),
    aws_role_name=getenv('AWS_ROLE_NAME'),
    aws_region=getenv('AWS_REGION')
)

# get token
sa_token, _ = token_service.get_token()

# todo: unit test v4 signature

def test_token_type():
    """
    token will be dict if the call failed
    """
    assert isinstance(sa_token, str)


def test_token_signature():
    """
    This will fail if we get an invalid token or another error
    """
    assert "ya29" in sa_token[0:4]

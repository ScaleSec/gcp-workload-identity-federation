"""
A collect of unit tests
for failures.
"""

import logging
from os import getenv
from os.path import join, dirname

from dotenv import load_dotenv #pylint: disable=import-error
from scalesec_gcp_workload_identity.main import TokenService #pylint: disable=import-error
import pytest #pylint: disable=import-error
from botocore.exceptions import ClientError #pylint: disable=import-error
from requests.exceptions import HTTPError #pylint: disable=import-error

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('gcp_token_federation').setLevel(logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# load values from env
dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path=dotenv_path)

# init the token service
no_role_token_service = TokenService(
    gcp_project_number=getenv('GCP_PROJECT_NUMBER'),
    gcp_workload_id=getenv('GCP_WORKLOAD_ID'),
    gcp_workload_provider=getenv("GCP_WORKLOAD_PROVIDER"),
    gcp_service_account_email=getenv('GCP_SERVICE_ACCOUNT_EMAIL'),
    aws_account_id=getenv('AWS_ACCOUNT_ID'),
    aws_role_name='dlksdjfljsdkfsd',
    aws_region=getenv('AWS_REGION')
)

no_provider_token_service = TokenService(
    gcp_project_number=getenv('GCP_PROJECT_NUMBER'),
    gcp_workload_id=getenv('GCP_WORKLOAD_ID'),
    gcp_workload_provider="badprovider",
    gcp_service_account_email=getenv('GCP_SERVICE_ACCOUNT_EMAIL'),
    aws_account_id=getenv('AWS_ACCOUNT_ID'),
    aws_role_name=getenv('AWS_ROLE_NAME'),
    aws_region=getenv('AWS_REGION')
)

def test_no_role():
    """
    This should raise a ClientError exception because no role was provided
    """
    with pytest.raises(ClientError):
        sa_token, _ = no_role_token_service.get_token() #pylint: disable=unused-variable

def test_federation_failure():
    """
    This should return a 400, HTTPError because the federation call failed
    """
    with pytest.raises(HTTPError):
        sa_token, _ = no_provider_token_service.get_token() #pylint: disable=unused-variable

import logging
from os import getenv
from os.path import join, dirname

from dotenv import load_dotenv
from scalesec_gcp_workload_identity.main import TokenService

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('gcp_token_federation').setLevel(logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# load values from env
dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path=dotenv_path)

# init the token service
token_service = TokenService(
  gcp_project_number=getenv('gcp_project_number'),
  gcp_workload_id=getenv('gcp_workload_id'),
  gcp_workload_provider=getenv('gcp_workload_provider'),
  gcp_service_account_email=getenv('gcp_service_account_email'),
  aws_account_id=getenv('aws_account_id'),
  aws_role_name=getenv('aws_role_name'),
  aws_region=getenv('aws_region')
)

# get token
sa_token, _ = token_service.get_token()

# todo: unit test v4 signature

def test_token_type():
  assert type(sa_token) is str

def test_token_signature():
  """
  This will fail if we get an invalid token or another error
  """
  assert "ya29" in sa_token[0:4]
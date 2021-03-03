import datetime
import logging
from typing import Tuple
from botocore.credentials import ReadOnlyCredentials
from scalesec_gcp_workload_identity.utils import Utils

logger = logging.getLogger(__name__)

class TokenService:
    def __init__(self, gcp_project_number: str, gcp_workload_id: str, gcp_workload_provider:str, gcp_service_account_email: str, aws_account_id: str, aws_role_name: str, aws_region: str) -> None:
        # GCP
        self.gcp_project_number = gcp_project_number
        self.gcp_workload_id = gcp_workload_id
        self.gcp_provider = gcp_workload_provider
        self.gcp_service_account_email = gcp_service_account_email

        self.gcp_federated_token = None
        self.gcp_sa_token = None
        self.authorization_header = None
        
        # AWS 
        self.method = "POST"
        self.host = "sts.amazonaws.com"
        self.aws_account_id = aws_account_id
        self.aws_role_name = aws_role_name
        self.aws_region = aws_region

        self.x_goog_cloud_target_resource = f"//iam.googleapis.com/projects/{self.gcp_project_number}/locations/global/workloadIdentityPools/{self.gcp_workload_id}/providers/{self.gcp_provider}"

        # Utils class
        self.utils = Utils(self.aws_account_id, self.aws_role_name, self.aws_region, self.method, self.host, self.gcp_service_account_email)

    # TODO? is this really needed?
    def __repr__(self):
        return f"TokenService({self.gcp_sa_token!r})"

    def __str__(self):
        return f"TokenService: {self.gcp_sa_token}"

    def get_token(self) -> Tuple[str, str]:
        """
        Return a GCP Service Account Token
        """
        aws_access_key, aws_secret_access_key, aws_session_token = self.utils._assume_role()

        # create a ReadOnlyCredentials object with the assume_role credentials
        credentials = ReadOnlyCredentials(aws_access_key, aws_secret_access_key, aws_session_token)

        # Generate time used for signature
        # It seems if too much time passes between generation and use, the signature check will fail (<10% of the time)
        t = datetime.datetime.utcnow()
        x_amz_date = t.strftime('%Y%m%dT%H%M%SZ')

        # create the Authorization header
        authorization_header = self.utils._generate_auth_header(x_amz_date, credentials)
        
        # generate the identity token
        caller_identity_token = self.utils._generate_caller_identity_token(authorization_header, x_amz_date, self.x_goog_cloud_target_resource, credentials)

        # get the federated token from GCP
        federated_access_token = self.utils._get_federated_access_token(caller_identity_token, self.x_goog_cloud_target_resource)

        # get the SA token
        self.gcp_sa_token, sa_expire_time = self.utils._get_sa_token(federated_access_token)

        return self.gcp_sa_token, sa_expire_time


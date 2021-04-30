"""
main.py + utils.py are used to generate
our access token.
"""
import datetime
import logging
from typing import Tuple
from botocore.credentials import ReadOnlyCredentials #pylint: disable=import-error
from scalesec_gcp_workload_identity.utils import Utils

logger = logging.getLogger(__name__)

class TokenService: #pylint: disable=too-many-instance-attributes
    """
    Contains all vars and functions.
    """
    def __init__( #pylint: disable=too-many-arguments
        self,
        gcp_project_number: str,
        gcp_workload_id: str,
        gcp_workload_provider:str,
        gcp_service_account_email: str,
        aws_account_id: str,
        aws_role_name: str,
        aws_region: str,
        gcp_token_lifetime: str = "3600s"
        ) -> None:

        # GCP
        self.gcp_project_number = gcp_project_number
        self.gcp_workload_id = gcp_workload_id
        self.gcp_provider = gcp_workload_provider
        self.gcp_service_account_email = gcp_service_account_email
        self.gcp_token_lifetime = gcp_token_lifetime

        self.gcp_federated_token = None
        self.gcp_sa_token = None
        self.authorization_header = None

        # AWS
        self.method = "POST"
        self.host = "sts.amazonaws.com"
        self.aws_account_id = aws_account_id
        self.aws_role_name = aws_role_name
        self.aws_region = aws_region

        self.x_goog_cloud_target_resource = f"//iam.googleapis.com/projects/{self.gcp_project_number}/locations/global/workloadIdentityPools/{self.gcp_workload_id}/providers/{self.gcp_provider}" #pylint: disable=line-too-long

        # Utils class
        self.utils = Utils(
            self.aws_account_id,
            self.aws_role_name,
            self.aws_region,
            self.method,
            self.host,
            self.gcp_service_account_email
            )

    def __repr__(self):
        return f"TokenService({self.gcp_sa_token!r})"

    def __str__(self):
        return f"TokenService: {self.gcp_sa_token}"

    def get_token(self) -> Tuple[str, str]:
        """
        Return a GCP Service Account Access Token
        """

        aws_access_key, aws_secret_access_key, aws_session_token = self.utils._assume_role() #pylint: disable=protected-access

        # create a ReadOnlyCredentials object with the assume_role credentials
        credentials = ReadOnlyCredentials(aws_access_key, aws_secret_access_key, aws_session_token)

        # Generate time used for signature
        # It seems if too much time passes between generation and use, the signature check will fail (<10% of the time) #pylint: disable=line-too-long
        current_time = datetime.datetime.utcnow()
        x_amz_date = current_time.strftime('%Y%m%dT%H%M%SZ')

        # create the Authorization header
        authorization_header = self.utils._generate_auth_header(x_amz_date, credentials) #pylint: disable=protected-access

        # generate the identity token
        caller_identity_token = self.utils._generate_caller_identity_token( #pylint: disable=protected-access
            authorization_header,
            x_amz_date,
            self.x_goog_cloud_target_resource,
            credentials
            )

        # get the federated token from GCP
        federated_access_token = self.utils._get_federated_access_token( #pylint: disable=protected-access
            caller_identity_token,
            self.x_goog_cloud_target_resource
            )

        # get the SA token
        self.gcp_sa_token, sa_expire_time = self.utils._get_sa_token(federated_access_token, self.gcp_token_lifetime) #pylint: disable=protected-access

        return self.gcp_sa_token, sa_expire_time

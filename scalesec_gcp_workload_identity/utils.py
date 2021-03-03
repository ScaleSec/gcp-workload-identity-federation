import json
import logging
from sys import exit
from typing import Tuple
import urllib.parse

import boto3
from botocore import exceptions
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import requests


logger = logging.getLogger(__name__)


class BearerAuth(requests.auth.AuthBase):
    """
    Returns a requests authorization object with the bearer token
    """
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class Utils:
    def __init__(self, aws_account_id: str, aws_role_name: str, aws_region: str, method: str, host: str, gcp_service_account_email: str) -> None:

        # Init STS client
        self.sts_client = boto3.client('sts')

        self.aws_account_id = aws_account_id
        self.aws_role_name = aws_role_name
        self.aws_region = aws_region
        self.method = method
        self.host = host
        self.gcp_service_account_email = gcp_service_account_email

        # STS url for GetCallerIdentity
        self.url = 'https://sts.amazonaws.com?Action=GetCallerIdentity&Version=2011-06-15'

    def _assume_role(self) -> Tuple[str, str, str]:
        """
        Assumes the AWS IAM role used for federation
        """

        # Assume CopyCat IAM role
        try:
            logger.info("Assuming GCP CopyCat IAM Role.")
            assumed_role_object: dict = self.sts_client.assume_role(
                RoleArn=f"arn:aws:iam::{self.aws_account_id}:role/{self.aws_role_name}",
                RoleSessionName=self.aws_role_name
            )
        except exceptions.ClientError as err:
            logger.fatal(err)
            exit(1)

        # Capture temporary credentials
        credentials: dict = assumed_role_object['Credentials']

        # Create our temporay credentials to use in our SigV4 
        # Caller Identity Token signing process
        aws_access_key: str = credentials['AccessKeyId']
        aws_secret_access_key: str = credentials['SecretAccessKey']
        aws_session_token: str = credentials['SessionToken']

        return aws_access_key, aws_secret_access_key, aws_session_token

    def _signed_request(self, data=None, params=None, headers=None, credentials=None) -> str:
        """
        Function to sign a request using botocore implementation
        """
        request = AWSRequest(method=self.method, url=self.url, data=data, params=params, headers=headers)

        # inject auth header into requests object
        # SigV4Auth will split the query string automatically
        SigV4Auth(credentials, "sts", self.aws_region).add_auth(request)

        # return the auth object as thats the only thing we care about
        auth_headers = request.headers['Authorization']

        return auth_headers

    def _generate_auth_header(self, x_amz_date, credentials) -> str:
        """
        Create the authentication header needed by GCP
        """

        # these are the headers we want signed
        headers = {'host': self.host, 'x-amz-date': x_amz_date,'x-amz-security-token': credentials.token}
        
        # create the signed request which will return the Authorization header
        signature = self._signed_request(params=None, data=None, headers=headers, credentials=credentials)

        return signature
    
    def _generate_caller_identity_token(self, authorization_header, x_amz_date, x_goog_cloud_target_resource, credentials):
        """
        Create our Get Caller Identity Token object to be used by GCP
        """
        identity_token = {
            "url": "https://sts.amazonaws.com?Action=GetCallerIdentity&Version=2011-06-15",
            "method": self.method,
            "headers": [
                {
                "key": "Authorization",
                "value" : authorization_header
                },
                {
                "key": "host",
                "value": self.host
                },
                {
                "key": "x-amz-date",
                "value": x_amz_date
                },
                {
                "key": "x-goog-cloud-target-resource",
                "value": x_goog_cloud_target_resource
                },
                {
                "key": "x-amz-security-token",
                "value": credentials.token
                }
            ],
        }

        return identity_token

    def _get_federated_access_token(self, caller_identity_token: dict, x_goog_cloud_target_resource: str) -> str:
        """
        Exchange our Caller Identity Token for a GCP federated token

        Returns:

            response: str - the federated access token
        """
        # token json must be url encoded
        encoded_token: str = urllib.parse.quote(json.dumps(caller_identity_token))

        # Create the body for our token exchange request
        body = {
            "audience": x_goog_cloud_target_resource,
            "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
            "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
            "scope": "https://www.googleapis.com/auth/cloud-platform",
            "subjectTokenType": "urn:ietf:params:aws:token-type:aws4_request",
            "subjectToken": encoded_token
        }

        # Add json headers and send the request
        headers = {"content-type": "application/json; charset=utf-8"}

        response = requests.post("https://sts.googleapis.com/v1beta/token", json=body, headers=headers)
        try:
            federated_token: str = response.json()['access_token']
        except KeyError:
            logger.fatal("Failed to get federated token")
            logger.error(response.text)
            exit(1)
        return federated_token
    
    def _get_sa_token(self, federated_token) -> Tuple[str, str]:
        """
        Exchanges a federated token (limited service support) for a a better supported SA token

        Returns:
            accessToken

            expireTime
        """

        # Create the body for our token exchange request
        body = {
            "scope": [
                "https://www.googleapis.com/auth/cloud-platform"
            ]
        }

        # Add json headers and send the request
        headers = {"content-type": "application/json; charset=utf-8", "Accept": "application/json"}

        response = requests.post(f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{self.gcp_service_account_email}:generateAccessToken", json=body, headers=headers, auth=BearerAuth(federated_token))

        if response.status_code != 200:
            logger.fatal("Error getting SA token")
            logger.error(response.text)
            exit(1)

        data = response.json()
        return data['accessToken'], data['expireTime']
"""
This is an example script
to generate a SA access token
and list available GKE clusters.
"""

from os import getenv
from scalesec_gcp_workload_identity.main import TokenService #pylint: disable=import-error


def main():
    """
    Generates a token and
    lists GKE clusters.
    """

    # The arguments to TokenService can be ingested
    # from the environment if they were exported above.
    # Otherwise, pass in your own arguments
    token_service = TokenService(
        gcp_project_number=getenv('GCP_PROJECT_NUMBER'),
        gcp_workload_id=getenv('GCP_WORKLOAD_ID'),
        gcp_workload_provider=getenv('GCP_WORKLOAD_PROVIDER'),
        gcp_service_account_email=getenv('GCP_SERVICE_ACCOUNT_EMAIL'),
        aws_account_id=getenv('AWS_ACCOUNT_ID'),
        aws_role_name=getenv('AWS_ROLE_NAME'),
        aws_region=getenv('AWS_REGION')
    )

    # Return our GCP SA access token
    # This sa_token is used for listing our GKE clusters
    sa_token, expiry_date = token_service.get_token() #pylint: disable=unused-variable

    print(f"The service account OAuth token is: \n {sa_token}")

if __name__ == "__main__":
    main()

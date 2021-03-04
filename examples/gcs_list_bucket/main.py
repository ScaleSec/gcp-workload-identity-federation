#!/usr/bin/python3

from scalesec_gcp_workload_identity.main import TokenService
from os import getenv
from google.cloud import storage 
from google.api_core import exceptions # pylint: disable=import-error



def main():

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
    # This sa_token is used for listing objects in our bucket
    sa_token, expiry_date = token_service.get_token()

    # Create the GCS client with our newly generated SA token
    storage_client = storage.Client(credentials = f"{sa_token}")

    # The name for the new bucket 
    # Export this as an environment variable
    bucket_name = getenv("BUCKET_NAME")

    # List objects in our bucket using our GCP SA Access token
    try:
        files = storage_client.list_blobs(bucket_name)
        print(f"Files in {bucket_name} are: {files}")
    except Exception as e:
        print(e)
        raise

if __name__ == "main":
    main()

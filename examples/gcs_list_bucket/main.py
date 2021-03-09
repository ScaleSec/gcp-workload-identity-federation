#!/usr/bin/env python

from scalesec_gcp_workload_identity.main import TokenService
from os import getenv
from google.api_core import exceptions
import requests
import json

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

    # The name for the bucket we want to list object in
    # Export this as an environment variable
    bucket_name = getenv("BUCKET_NAME")

    # List objects in our bucket using our GCP SA Access token
    try:
        files = requests.get(
            f'https://storage.googleapis.com/storage/v1/b/{bucket_name}/o/?fields=items/name',
            params={'access_token': sa_token}).json()
    except Exception as e:
        print(e)
        raise
    
    # Make our object names pretty!
    object_names = json.dumps(files, indent=4)
    
    # Print our object names found in our bucket 
    print(f"The items in bucket {bucket_name} are: {object_names}")

if __name__ == "__main__":
    main()
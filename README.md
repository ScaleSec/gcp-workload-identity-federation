# Scalesec GCP Workload Identity Federation

This package provides a python module to federate access from AWS to GCP using Workload Identity

## Quick start

```shell
# Create venv and install package
make setup
source .venv/bin/activate
pip install scalesec-gcp-workload-identity
```

```shell
# set up GCP credentials
gcloud auth login

# Enable the STS service in the project
gcloud services enable sts.googleapis.com

# The values below should be exported into the environment to be reused when calling the module later

# Create the GCP Workload Identity Pool
gcloud beta iam workload-identity-pools create "$gcp_workload_id" \
  --location="global" \
  --description="$gcp_workload_id" \
  --display-name="$gcp_workload_id"

# Create the GCP Workload Identity AWS Provider
gcloud beta iam workload-identity-pools providers create-aws "$gcp_workload_provider" \
  --location="global" \
  --workload-identity-pool="$gcp_workload_id" \
  --account-id="$aws_account_id" 

# Add the appropriate IAM binding to a pre-existing service account
gcloud iam service-accounts add-iam-policy-binding $gcp_service_account_email \
  --role roles/iam.workloadIdentityUser \
  --member "principalSet://iam.googleapis.com/projects/$gcp_project_number/locations/global/workloadIdentityPools/$gcp_workload_id/attribute.aws_role/arn:aws:sts::${aws_account_id}:assumed-role/$aws_role_name"
```

### Using the module

Set your AWS credentials
```shell
export AWS_PROFILE=xyz
```

Getting a Service Account token is now simple:

```python
from scalesec_gcp_workload_identity.main import TokenService

token_service = TokenService(args...)
sa_token, expiry_date = token_service.get_token()
```

The arguments to TokenService can be ingested from the environment if they were exported above:

```python
from os import getenv

token_service = TokenService(
  gcp_project_number=getenv('gcp_project_number'),
  gcp_workload_id=getenv('gcp_workload_id'),
  gcp_workload_provider=getenv('gcp_workload_provider'),
  gcp_service_account_email=getenv('gcp_service_account_email'),
  aws_account_id=getenv('aws_account_id'),
  aws_role_name=getenv('aws_role_name'),
  aws_region=getenv('aws_region')
)
```

## Testing

```shell
# make a venv
make setup
```

Edit `.env` with your values

```shell
# install deps
make dev

# run pytest
make test
```

## Upload to PyPi

Set your token/credentials in ~/.pypirc

`make dist VERSION=1.x.x`
# Scalesec GCP Workload Identity Federation

This package provides a python module to federate access from AWS to GCP using Workload Identity.

## Prerequisites 
* A GCP service account 
* python3.x

## Quick start

```shell
# Create venv and install package
make setup
source .venv/bin/activate
pip install scalesec-gcp-workload-identity
```

```shell
# Rename example .env
mv .env.example .env

# Enter your own environment variables
cat <<EOF >.env
export GCP_PROJECT_NUMBER=
export GCP_PROJECT_ID=
export GCP_WORKLOAD_ID=
export GCP_WORKLOAD_PROVIDER=
export GCP_SERVICE_ACCOUNT_EMAIL=
export AWS_REGION=
export AWS_ACCOUNT_ID=
export AWS_ROLE_NAME=
EOF

# Source the environment variables so they are exposed
source .env
```

```shell
# set up GCP credentials
gcloud auth login

# Configure the default project
gcloud config set project $GCP_PROJECT_ID

# Enable the STS service in the project
gcloud services enable sts.googleapis.com

# Enable the IAM credentials service
gcloud services enable iamcredentials.googleapis.com

# The following commands use the .env values

# Create the GCP Workload Identity Pool
gcloud beta iam workload-identity-pools create "$GCP_WORKLOAD_ID" \
  --location="global" \
  --description="$GCP_WORKLOAD_ID" \
  --display-name="$GCP_WORKLOAD_ID"

# Create the GCP Workload Identity AWS Provider
gcloud beta iam workload-identity-pools providers create-aws "$GCP_WORKLOAD_PROVIDER" \
  --location="global" \
  --workload-identity-pool="$GCP_WORKLOAD_ID" \
  --account-id="$AWS_ACCOUNT_ID" 

# Add the appropriate IAM binding to a pre-existing service account
gcloud iam service-accounts add-iam-policy-binding $GCP_SERVICE_ACCOUNT_EMAIL \
  --role roles/iam.workloadIdentityUser \
  --member "principalSet://iam.googleapis.com/projects/$GCP_PROJECT_NUMBER/locations/global/workloadIdentityPools/$GCP_WORKLOAD_ID/attribute.aws_role/arn:aws:sts::${AWS_ACCOUNT_ID}:assumed-role/$AWS_ROLE_NAME"
```

### Using the module

Set your AWS credentials

```shell
export AWS_PROFILE=xyz
```

Getting a Service Account token is now simple:

```python
from scalesec_gcp_workload_identity.main import TokenService
from os import getenv

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

sa_token, expiry_date = token_service.get_token()
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

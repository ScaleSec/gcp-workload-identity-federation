# Scalesec GCP Workload Identity Federation

[![.github/workflows/python-linter.yml](https://github.com/ScaleSec/gcp-workload-identity-federation/actions/workflows/python-linter.yml/badge.svg)](https://github.com/ScaleSec/gcp-workload-identity-federation/actions/workflows/python-linter.yml) [![CodeQL](https://github.com/ScaleSec/gcp-workload-identity-federation/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/ScaleSec/gcp-workload-identity-federation/actions/workflows/codeql-analysis.yml)

This package provides a python module to federate access from AWS to GCP using Workload Identity. View our [blog](https://scalesec.com/blog/access-gcp-from-aws-using-workload-identity-federation/) for additional details.

## Prerequisites
* A GCP service account (environment variable "GCP_SERVICE_ACCOUNT_EMAIL")
* An AWS IAM role (environment variable "AWS_ROLE_NAME")
* AWS credentials (environment variable "AWS_PROFILE")
* python3.x

## Quick start

```bash
# Create venv and install package
make setup
source .venv/bin/activate
pip install scalesec-gcp-workload-identity
```

```bash
# Rename example .env
mv .env.example .env
```

```bash
# Enter your own environment variables
cat <<EOF >.env
# GCP
export GCP_PROJECT_NUMBER=
export GCP_PROJECT_ID=

# gcp workload identity pool id
export GCP_WORKLOAD_ID=
export GCP_WORKLOAD_PROVIDER=
export GCP_SERVICE_ACCOUNT_EMAIL=

# aws
export AWS_REGION=
export AWS_ACCOUNT_ID=
export AWS_ROLE_NAME=

# Token expiry
export TOKEN_LIFETIME=
EOF
```

```bash
# Source the environment variables so they are exposed
source .env
```

```bash
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

```bash
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
  aws_region=getenv('AWS_REGION'),
  gcp_token_lifetime=getenv('TOKEN_LIFETIME')
)

sa_token, expiry_date = token_service.get_token()
```

### Token expiration

The default expiration for a service account token is 1h in GCP. This behavior can be changed by overriding the environment variable `TOKEN_LIFETIME` in the `.env` file. By default, GCP does not allow tokens to have an expiry over 1 hour and an organization policy __must__ be updated for this change to take affect. The organization policy is called `iam.allowServiceAccountCredentialLifetimeExtension` and it accepts a list of service accounts that are allowed to have an > 1 hr token.

```bash
# To configure the organization policy
gcloud org-policies set-policy policy.yaml

# An example policy.json:
name: projects/1234567890/policies/iam.allowServiceAccountCredentialLifetimeExtension
spec:
  etag: BwXBMNmIrQg=
  rules:
  - values:
      allowedValues:
      - your-sa@yourproject.iam.gserviceaccount.com
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

## Local Linting

To test that your code will pass the lint and code quality GitHub action:

* Clone the repository locally
* Make your updates
* From the root of the repository, execute:
```bash
pylint --rcfile .github/workflows/configs/.pylintrc scalesec_gcp_workload_identity tests examples
```

## Examples

We have provided [examples](./examples) on how to use the service account access token generated by this module. Access tokens are mainly used via an API call or using `curl` on the CLI.

## Restricting Identity Pool Providers

By default, any GCP user with the `roles/iam.workloadIdentityPoolAdmin` or `roles/owner` role is able to create a workload identity pool in your GCP organization. There are two organization policies available to help you lockdown which outside providers can have pools in your organization.

* `constraints/iam.workloadIdentityPoolProviders ` - Accepts a list of URIs such as `https://sts.amazonaws.com` or `https://sts.windows.net/$AZURE_TENANT_ID`. For example:

```bash
# Allows all AWS accounts but no Azure or OIDC
gcloud beta resource-manager org-policies allow constraints/iam.workloadIdentityPoolProviders \
     https://sts.amazonaws.com --organization=$ORG_ID

# Allows only a specific Azure tenant but no AWS or OIDC
gcloud beta resource-manager org-policies allow constraints/iam.workloadIdentityPoolProviders \
     https://sts.windows.net/$AZURE_TENANT_ID --organization=$ORG_ID
```

* `constraints/iam.workloadIdentityPoolAwsAccounts` - Specifically focused on AWS, this constraint accepts a list of AWS account IDs. If this orgnanization policy is used, `constraints/iam.workloadIdentityPoolProviders` must either allow `https://sts.amazonaws.com` or be set to default (allow all). For example:

```bash
# Only allows a specific AWS account
gcloud beta resource-manager org-policies allow constraints/iam.workloadIdentityPoolAwsAccounts \
    $AWS_ACCOUNT_ID --organization=$ORG_ID
```

## Upload to PyPi

Set your token/credentials in ~/.pypirc

`make dist VERSION=1.x.x`

## Feedback

Feedback is welcome and encouraged via a GitHub issue. Please open an issue for any bugs, feature requests, or general improvements you would like to see. Thank you in advance!

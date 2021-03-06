# GCS list objects

This example uses the service account OAuth access token as an access token in an API request using the `requests` python library.

Before using this example, follow the [README](../../README.md) to configure your environment properly.

## Example Overview:

We generate our access token:
```python
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

Using the `requests` library we can pass in our ephemeral service account token `sa_token` in the parameters field:

```python
requests.get(
    f'https://storage.googleapis.com/storage/v1/b/{bucket_name}/o/?fields=items/name',
    params={'access_token': sa_token}).json()
```

The full code example can be found in [main.py](./main.py)
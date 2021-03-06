# GKE list clusters with curl

This example uses the service account OAuth access token as an authorization bearer in a curl request. 

Before using this example, follow the [README](../../README.md) to configure your environment properly.

## Example Overview:

We generate our access token and print it to stdout:
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

    print(f"The service account OAuth token is: \n {sa_token}")
```

Using our output, we add the `access_token` value into a `curl` command on our cli:

```bash
curl -H "Authorization: Bearer $ACCESS_TOKEN" "https://container.googleapis.com/v1/projects/$GCP_PROJECT_ID/zones/$ZONE/clusters"
```
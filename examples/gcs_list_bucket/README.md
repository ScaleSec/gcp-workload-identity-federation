# GCS List Objects

This example uses the service account OAuth access token as an access token in an API request using the `requests` python library.

Using the `requests` library we can pass in our ephemeral service account token in the parameters field:


```python
requests.get(
    f'https://storage.googleapis.com/storage/v1/b/{bucket_name}/o/?fields=items/name',
    params={'access_token': sa_token}).json()
```

The full code example can be found in [main.py](./main.py)
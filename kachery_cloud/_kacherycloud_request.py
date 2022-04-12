import requests
from datetime import datetime
from .get_client_id import get_client_id
from ._client_keys import _sign_message_as_client
from ._kachery_cloud_api_url import _kachery_cloud_api_url

def _kacherycloud_request(request_payload: dict):
    client_id = get_client_id()
    url = f'{_kachery_cloud_api_url}/api/kacherycloud'
    timestamp = int(datetime.timestamp(datetime.now()) * 1000)
    payload = {**request_payload, **{'timestamp': timestamp}}
    req = {
        'payload': payload,
        'fromClientId': client_id,
        'signature': _sign_message_as_client(payload)
    }
    resp = requests.post(url, json=req)
    if resp.status_code != 200:
        raise Exception(f'Error in {payload["type"]} ({resp.status_code}) {resp.reason}: {resp.text}')
    response = resp.json()
    return response
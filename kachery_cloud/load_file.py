import os
from typing import Union
import requests
import random
from .get_kachery_cloud_dir import get_kachery_cloud_dir
from ._kacherycloud_request import _kacherycloud_request


def load_file(uri: str, *, verbose: bool=False) -> Union[str, None]:
    if uri.startswith('/'):
        if os.path.exists(uri):
            return uri
        else:
            raise Exception(f'File does not exist: {uri}')
    if uri.startswith('sha1://'):
        return load_file_local(uri)
    assert uri.startswith('ipfs://'), f'Invalid or unsupported URI: {uri}'
    a = uri.split('?')[0].split('/')
    assert len(a) >= 3, f'Invalid or unsupported URI: {uri}'
    cid = a[2]

    kachery_cloud_dir = get_kachery_cloud_dir()
    e = cid[-6:]
    parent_dir = f'{kachery_cloud_dir}/ipfs/{e[0]}{e[1]}/{e[2]}{e[3]}/{e[4]}{e[5]}'
    filename = f'{parent_dir}/{cid}'
    if os.path.exists(filename):
        return filename

    payload = {
        'type': 'findIpfsFile',
        'cid': cid
    }
    response= _kacherycloud_request(payload)
    found = response['found']
    if found:
        url = response['url']
    else:
        raise Exception(f'File not found: {uri}')
        # url = f'https://{cid}.ipfs.dweb.link'
        # url = f'https://cloudflare-ipfs.com/ipfs/{cid}'
        # url = f'https://ipfs.filebase.io/ipfs/{cid}'

    if verbose:
        print(f'Loading file from kachery cloud: {uri}')    
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
    tmp_filename = f'{filename}.tmp.{_random_string(8)}'
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(tmp_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    try:
        os.rename(tmp_filename, filename)
    except:
        if not os.path.exists(filename): # maybe some other process beat us to it
            raise Exception(f'Unexpected problem moving file {tmp_filename}')
    return filename

def load_file_local(uri: str):
    assert uri.startswith('sha1://'), f'Invalid local URI: {uri}'
    a = uri.split('?')[0].split('/')
    assert len(a) >= 3, f'Invalid or unsupported URI: {uri}'
    sha1 = a[2]

    kachery_cloud_dir = get_kachery_cloud_dir()

    s = sha1
    parent_dir = f'{kachery_cloud_dir}/sha1/{s[0]}{s[1]}/{s[2]}{s[3]}/{s[4]}{s[5]}'
    filename = f'{parent_dir}/{sha1}'
    if os.path.exists(filename):
        return filename
    else:
        raise Exception(f'Unable to find local file: {uri}')

def _random_string(num_chars: int) -> str:
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(num_chars))
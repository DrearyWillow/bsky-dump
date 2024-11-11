#!/usr/bin/env python

import requests
import json
from datetime import datetime, timedelta, timezone
import sys

credentials = {
    'username': "",
    'password': ""
}

def get_session():
    url = 'https://bsky.social/xrpc/com.atproto.server.createSession'

    payload = {
        'identifier': credentials["username"],
        'password': credentials["password"]
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get access token. Status code: {response.status_code}. Response: {response.text}")
        
def get_service_endpoint(did):
    url = f"https://plc.directory/{did}"
    response = requests.get(url)
    if response.status_code == 200:
        services = response.json().get('service')
        for service in services:
            if service['type'] == 'AtprotoPersonalDataServer':
                return service['serviceEndpoint']
        raise Exception("PDS serviceEndpoint not found in DID document.")
    else:
        raise Exception(f"Failed to get DID document. Status code: {response.status_code}. Response: {response.text}")

def url2uri(post_url):
    parts = post_url.rstrip('/').split('/')
    if len(parts) < 6: raise ValueError(f"Post URL '{post_url}' does not have enough segments.")
    handle, rkey = parts[4], parts[6]
    did = resolve_did(handle)
    return f"at://{did}/app.bsky.feed.post/{rkey}", rkey, did

def resolve_did(handle):
    if handle.startswith("did:"): return handle 
    response = requests.get(f'https://public.api.bsky.app/xrpc/com.atproto.identity.resolveHandle?handle={handle}')
    if response.status_code != 200: raise Exception(f"Failed to resolve DID: '{response.text}'")
    return response.json()['did']

def get_post_thread(at_uri):
    params = {'uri': at_uri, 'depth': 1, 'parentHeight': 0}
    response = requests.get('https://public.api.bsky.app/xrpc/app.bsky.feed.getPostThread', headers={'Content-Type': 'application/json'}, params=params)
    if response.status_code != 200: raise Exception(f"Failed to retrieve post thread: '{response.text}'")
    return response.json().get('thread')

def replace_post(text, session, rkey, url_did, at_uri, thread):
    # service_endpoint = "https://magic.us-west.host.bsky.network"
    if url_did != (did := session.get('did')):
        print(f"Post did '{url_did}' does not match session did '{did}'. Fix login details.")
        return
    service_endpoint = get_service_endpoint(did)
    # service_endpoint = "https://bsky.social"
    url = f"{service_endpoint}/xrpc/com.atproto.repo.putRecord"

    # thread = get_post_thread(at_uri)

    swap_record = thread.get('post').get('cid')
    print(f"Latest CID: {swap_record}")

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    # now = thread.get('post').get('record').get('createdAt')

    post = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now,
    }

    payload = json.dumps({
    "repo": did,
    "collection": "app.bsky.feed.post",
    "rkey": rkey,
    # "validate": True,
    "record": post,
    "swapRecord": swap_record
    # "swapRecord": "bafyreicrbqff7ck5glmybtuswf3vu6fcmjpqbcoalryttchgc3idn5aanm",
    # "swapCommit": "bafyreife2acril4stsmbphty3naxsh6khvdgmbrqh6nyjfyhzrp7in3iky"
    })

    print(payload)

    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {session.get('accessJwt')}'
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        rkey = response.json().get('uri').rstrip('/').split('/')[-1]
        print(f"Post created successfully: https://bsky.app/profile/{session.get('handle')}/post/{rkey}")
        print(json.dumps(response.json(), indent=3))
    else:
        raise Exception(f"Failed to create post. Status code: {response.status_code}. Response: {response.text}")

def delete_post(session, did, rkey):

    # url = "https://public.api.bsky.app/xrpc/com.atproto.repo.deleteRecord"
    service_endpoint = get_service_endpoint(did)
    url = f"{service_endpoint}/xrpc/com.atproto.repo.deleteRecord"
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {session.get('accessJwt')}'
    }
    payload = json.dumps({
    "repo": did,
    "collection": "app.bsky.feed.post",
    "rkey": rkey,
    # "validate": True,
    })
    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        # rkey = response.json().get('uri').rstrip('/').split('/')[-1]
        print(json.dumps(response.json(), indent=3))
        print(f"Post deleted successfully: https://bsky.app/profile/{session.get('handle')}/post/{rkey}")
    else:
        raise Exception(f"Failed to delete post. Status code: {response.status_code}. Response: {response.text}")


def main():
    post_url = input("Enter a post url: ") if len(sys.argv) <= 1 else sys.argv[1]
    text = input("Enter post text: ")

    at_uri, rkey, did = url2uri(post_url)

    thread = get_post_thread(at_uri)

    delete_post(get_session(), did, rkey)
    replace_post(text, get_session(), rkey, did, at_uri, thread)

if __name__ == "__main__":
    main()
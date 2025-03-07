#!/usr/bin/env python

import requests
import json
from datetime import datetime, timedelta, timezone
import sys
import mimetypes

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

# def get_image(session, blob_location):
#     # IMAGE_MIMETYPE = "image/png"
#     mime_type = mimetypes.guess_type(blob_location)
#     blob_type = mime_type.split('/')[0]

#     with open(blob_location, "rb") as f:
#         blob_bytes = f.read()

#     if len(blob_bytes) > 1000000:
#         raise Exception(
#             f"{blob_type} file size too large. 1000000 bytes maximum, got: {len(blob_bytes)}"
#         )

#     response = requests.post(
#         "https://bsky.social/xrpc/com.atproto.repo.uploadBlob",
#         headers={
#             "Content-Type": mime_type,
#             "Authorization": "Bearer " + session["accessJwt"],
#         },
#         data=blob_bytes,
#     )
#     response.raise_for_status()
#     return response.json()["blob"], blob_type

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

def delete_post(session, service_endpoint, did, rkey):
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
    })
    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        print(json.dumps(response.json(), indent=3))
        print(f"Post deleted successfully: https://bsky.app/profile/{session.get('handle')}/post/{rkey}")
    else:
        raise Exception(f"Failed to delete post. Status code: {response.status_code}. Response: {response.text}")


def replace_post(session, service_endpoint, did, rkey, record, text):
    # service_endpoint = "https://magic.us-west.host.bsky.network"
    url = f"{service_endpoint}/xrpc/com.atproto.repo.createRecord"

    # now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    # record = thread.get('post').get('record')
    # record["createdAt"] = now
    print("Before:")
    print(json.dumps(record, indent=3))
    record["text"] = text
    
    # with open('/home/kyler/Downloads/new.json', 'r') as file:
    #     record = json.load(file)
        
    payload = json.dumps({
    "repo": did,
    "collection": "app.bsky.feed.post",
    "validate": False,
    "rkey": rkey,
    "record": record,
    })

    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {session.get('accessJwt')}'
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        rkey = response.json().get('uri').rstrip('/').split('/')[-1]
        print(json.dumps(response.json(), indent=3))
        print(f"Post created successfully: https://bsky.app/profile/{session.get('handle')}/post/{rkey}")
    else:
        raise Exception(f"Failed to create post. Status code: {response.status_code}. Response: {response.text}")
        

def main():
    post_url = input("Enter a post url: ") if len(sys.argv) <= 1 else sys.argv[1]
    text = input("Enter post text: ")

    at_uri, rkey, post_did = url2uri(post_url)
    session = get_session()
    did = session.get('did')
    if did != post_did:
        print(f"Post DID '{url_did}' does not match session DID '{did}'.")
        return
    
    service_endpoint = get_service_endpoint(did)
    thread = get_post_thread(at_uri)

    delete_post(session, service_endpoint, did, rkey)
    replace_post(session, service_endpoint, did, rkey, thread.get('post').get('record'), text)

    # replace_post(session, service_endpoint, did, rkey)

if __name__ == "__main__":
    main()
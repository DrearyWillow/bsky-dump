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

def resolve_did(handle):
    if handle.startswith("did:"): return handle 
    response = requests.get(f'https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle={handle}')
    if response.status_code != 200: raise Exception(f"Failed to resolve DID: '{response.text}'")
    return response.json()['did']

def create_post(session):
    # service_endpoint = "https://magic.us-west.host.bsky.network"
    did = session.get('did')
    service_endpoint = get_service_endpoint(did)
    url = f"{service_endpoint}/xrpc/com.atproto.repo.createRecord"

    post = {
        "$type": "app.bsky.feed.post",
        "createdAt": "2024-11-23T14:34:23.572Z",
        "text": "dm leaks have confirmed that i am in fact aromantic"
    }
    # print(type(post))
    # print(post)
    # print(post["text"])
    # exit()

    payload = json.dumps({
    "repo": did,
    "collection": "app.bsky.feed.post",
    "record": post,
    "rkey": "3lbmpmoyo3s25"
    })

    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {session.get('accessJwt')}'
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        rkey = response.json().get('uri').rstrip('/').split('/')[-1]
        print(f"Post created successfully: https://bsky.app/profile/{session.get('handle')}/post/{rkey}")
    else:
        raise Exception(f"Failed to create post. Status code: {response.status_code}. Response: {response.text}")
        

def main():
    # arg_len = len(sys.argv)
    # text = input("Enter post text: ") if arg_len <= 1 else sys.argv[1]
    # parent_url = input("Enter a parent url: ") if arg_len <= 2 else sys.argv[2]
    # img_location = input("Enter an png location: ") if arg_len <= 3 or sys.argv[3] == "" else sys.argv[3]
    # if img_location != "":
    #     alt_text = input("Enter image alt text: ") if arg_len <= 4 else sys.argv[4]
    # else:
    #     alt_text = ""

    create_post(get_session())

if __name__ == "__main__":
    main()

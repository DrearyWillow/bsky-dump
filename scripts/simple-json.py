#!/usr/bin/env python

import requests
import subprocess
import sys
import json
from pathlib import Path
import re
from datetime import datetime

def url2uri(post_url):
    parts = post_url.rstrip('/').split('/')
    if len(parts) < 4: raise ValueError(f"Post URL '{post_url}' does not have enough segments.")
    rkey, username = parts[-1], parts[-3]
    return f"at://{resolve_did(username)}/app.bsky.feed.post/{rkey}"

def resolve_did(handle):
    if handle.startswith("did:"): return handle 
    response = requests.get(f'https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle={handle}')
    if response.status_code != 200: raise Exception(f"Failed to resolve DID: '{response.text}'")
    return response.json()['did']

def get_post_thread(post_url, reply_mode):
    at_uri = url2uri(post_url)
    params = {'uri': at_uri, 'depth': 1000 if reply_mode else 0, 'parentHeight': 1000 if reply_mode else 0}
    response = requests.get('https://public.api.bsky.app/xrpc/app.bsky.feed.getPostThread', headers={'Content-Type': 'application/json'}, params=params)
    if response.status_code != 200: raise Exception(f"Failed to retrieve post thread: '{response.text}'")
    return response.json()

def main():
    post_data = get_post_thread(post_url, reply_mode)
    print(json.dumps(post_data, indent=4))

if __name__ == "__main__":
    main()

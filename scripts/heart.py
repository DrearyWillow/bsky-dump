#!/usr/bin/env python

import requests
import sys
import re

def input_validation():
    if len(sys.argv) < 2:
        print("No url entered.")
        sys.exit(1)
    else:
        # parts = sys.argv[1].rstrip('/').split('/')[-1]
        # handle = parts[-1]
        return sys.argv[1].rstrip('/').split('/')[-1]

def get_did(handle):
    url = f"https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle={handle}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data.get('did')
    else:
        print(f"Failed to resolve DID. Status code: {response.status_code}, Message: {response.text}")
        sys.exit(1)

def get_bio(did):
    url = f"https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor={did}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        bio = data.get('description')
        return bio if bio else "No bio available"
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def extract_lovers(bio):
    # Regular expression to match @username surrounded by hearts or <3 with optional whitespace
    pattern = r"(❤️|<3)\s*@(\S+)\s*(❤️|<3)"
    match = re.search(pattern, bio)
    
    if match:
        return '@' + match.group(2)  # Return the @username (group 2 is the username part)
    else:
        return None

def main():
    try:
        handle = input_validation()
        bio = get_bio(get_did(handle))
        lover = extract_lovers(bio)
        if lover:
            lover_did = get_did(lover)
            print(lover_did)
        else:
            print("no bitches :(")
            return None
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()

#my_did = "did:plc:hx53snho72xoj7zqt5uice4u"
#test = 'at://did:plc:hx53snho72xoj7zqt5uice4u/app.bsky.feed.post/3l4372eftjc24'
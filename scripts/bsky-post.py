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

def get_image(session, blob_location):
    # IMAGE_MIMETYPE = "image/png"
    mime_type = mimetypes.guess_type(blob_location)
    blob_type = mime_type.split('/')[0]

    with open(blob_location, "rb") as f:
        blob_bytes = f.read()

    if len(blob_bytes) > 1000000:
        raise Exception(
            f"{blob_type} file size too large. 1000000 bytes maximum, got: {len(blob_bytes)}"
        )

    response = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.uploadBlob",
        headers={
            "Content-Type": mime_type,
            "Authorization": "Bearer " + session["accessJwt"],
        },
        data=blob_bytes,
    )
    response.raise_for_status()
    return response.json()["blob"], blob_type

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

def get_post_thread(post_url):
    at_uri = url2uri(post_url)
    params = {'uri': at_uri, 'depth': 1, 'parentHeight': 0}
    response = requests.get('https://public.api.bsky.app/xrpc/app.bsky.feed.getPostThread', headers={'Content-Type': 'application/json'}, params=params)
    if response.status_code != 200: raise Exception(f"Failed to retrieve post thread: '{response.text}'")
    return response.json().get('thread')

def create_post(text, session, parent_url, blob_location, alt_text):
    # service_endpoint = "https://magic.us-west.host.bsky.network"
    did = session.get('did')
    service_endpoint = get_service_endpoint(did)
    url = f"{service_endpoint}/xrpc/com.atproto.repo.createRecord"

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    # print(now)
    # exit()

    # now = datetime.now(timezone.utc) + timedelta(weeks=1)
    # now = now.isoformat().replace("+00:00", "Z")

    # now = datetime(1752, 9, 3, 8, 0, 0) # tzinfo=timezone.utc
    # now = now.isoformat().replace("+00:00", "Z")
    # print(now)
    # exit()

    #okay so it turns out tzinfo adds +00:00, if we call without, we need to add the Z ourselves
    # now = datetime(2023, 2, 29, 8, 0, 0)#, tzinfo=timezone.utc) # tzinfo=timezone.utc
    # now = now.isoformat().replace("+00:00", "") + "Z"
    # print(now)
    # exit()

    # now = "2023-02-29T18:00:00Z"

    # text = "arbitrary string"


    post = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now,
    }

    # post['facets'] = [
    #     {
    #         "features": [
    #             {
    #                 "$type": "app.bsky.richtext.facet#link",
    #                 "uri": "https://bsky.app/profile/did:plc:mbdv5fpty2wlssfwwpys2boh"
    #             }
    #         ],
    #         "index": {
    #             "byteEnd": 0,
    #             "byteStart": 300 
    #         }
    #     }
    # ]

    if parent_url != "":
        pdata = get_post_thread(parent_url)
        post['reply'] = {
            "parent": {
                "cid": pdata.get('post').get('cid'),
                "uri": pdata.get('post').get('uri'),
            },
            "root": {
                "cid": pdata.get('post').get('record').get('reply').get('root').get('cid'),
                "uri": pdata.get('post').get('record').get('reply').get('root').get('uri'),
            }
        }

    if blob_location != "":
        blob, blob_type = get_blob(session, blob_location)
        if blob_type not in ["image", "video"]:
            raise Exception(f"Unknown blob type '{blob_type}'")
        elif blob_type == "video":
            #https://docs.bsky.app/docs/api/app-bsky-video-upload-video
            #https://docs.bsky.app/docs/api/app-bsky-video-get-job-status
            #https://docs.bsky.app/docs/api/app-bsky-video-get-upload-limits
            # post['embed'] = {
            #     "$type": "app.bsky.embed.video",
            #     "video": [{
            #         "alt": alt_text,
            #         "video": blob,
            #     }],
            # }
            raise Exception("Video not supported yet.")
        elif blob_type == "image":
            post['embed'] = {
                "$type": "app.bsky.embed.images",
                "images": [{
                    "alt": alt_text,
                    "image": blob,
                }],
            }
        

    payload = json.dumps({
    "repo": did,
    "collection": "app.bsky.feed.post",
    "validate": True,
    "record": post,
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
    arg_len = len(sys.argv)
    text = input("Enter post text: ") if arg_len <= 1 else sys.argv[1]
    parent_url = input("Enter a parent url: ") if arg_len <= 2 else sys.argv[2]
    img_location = input("Enter an png location: ") if arg_len <= 3 or sys.argv[3] == "" else sys.argv[3]
    if img_location != "":
        alt_text = input("Enter image alt text: ") if arg_len <= 4 else sys.argv[4]
    else:
        alt_text = ""

    create_post(text, get_session(), parent_url, img_location, alt_text)

if __name__ == "__main__":
    main()
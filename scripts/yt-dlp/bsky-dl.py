#!/usr/bin/env python

import requests
import subprocess
import sys

defaults = {
    "username": '',
    "password": '',
    "default_dir": '/home/kyler/Downloads'
}

def input_validation():
    if len(sys.argv) < 2:
        print("No url entered.")
        sys.exit(1)
    else:
        input_url = sys.argv[1]
    if len(sys.argv) < 3:
        input_dir = defaults["default_dir"]
    else:
        input_dir = sys.argv[2]
    if len(sys.argv) > 3:
        json_print_mode = 1
    else:
        json_print_mode = 0
    if defaults["username"] == "":
        print("No username specified.")
        sys.exit(1)
    if defaults["password"] == "":
        print("No password specified.")
        sys.exit(1)
    return input_url, input_dir, json_print_mode

def get_access_token():
    CREATE_SESSION_URL = 'https://bsky.social/xrpc/com.atproto.server.createSession'
    payload = {
        'identifier': defaults["username"],
        'password': defaults["password"]
    }
    response = requests.post(CREATE_SESSION_URL, json=payload)
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('accessJwt')
        return access_token
    else:
        raise Exception(f"Failed to get access token. Status code: {response.status_code}, Message: {response.text}")

def url2uri(post_url):
    parts = post_url.rstrip('/').split('/')
    if len(parts) < 4:
        print("POST URL: " + post_url)
        raise ValueError("URL does not have enough segments.")
    username = parts[-3]
    authority = resolve_did(username)
    rkey = parts[-1]
    collection = 'app.bsky.feed.post'
    at_uri = f"at://{authority}/{collection}/{rkey}"
    return at_uri, rkey

def resolve_did(handle):
    resolve_url = 'https://bsky.social/xrpc/com.atproto.identity.resolveHandle'
    params = {'handle': handle}
    response = requests.get(resolve_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['did']
    else:
        raise Exception(f"Failed to resolve DID. Status code: {response.status_code}, Message: {response.text}")

def get_post_thread(post_url, access_token):
    BASE_URL = 'https://bsky.social/xrpc/app.bsky.feed.getPostThread'
    HEADERS = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    at_uri, rkey = url2uri(post_url)
    params = {'uri': at_uri, 'depth': 0}
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        return response.json(), rkey
    else:
        raise Exception(f"Failed to retrieve post thread. Status code: {response.status_code}, Message: {response.text}")

def download_video(post_data, path):
    # playlist_url = post_data['thread']['post']['embed']['playlist']
    playlist_url = post_data.get('thread', {}).get('post', {}).get('embed', {}).get('playlist', '')
    if not playlist_url:
        print(f"Post does not have a video embed.")
        exit()
    subprocess.run([
        'ffmpeg', '-i', playlist_url, '-c', 'copy', '-bsf:a', 'aac_adtstoasc', path
    ])

def main():
    try:
        post_url, directory, json_print_mode = input_validation()
        access_token = get_access_token()
        post_data, rkey = get_post_thread(post_url, access_token)
        if json_print_mode:
            print(post_data)
            exit()
        path = f"{directory}/{rkey}.mp4"
        download_video(post_data, path)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()



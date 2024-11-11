#!/usr/bin/env python

import requests
import subprocess
import sys
import json
from pathlib import Path
import re
try: 
    import streamlink
    dl_method = "streamlink"
except: 
    try:
        import yt_dlp
        dl_method = "yt-dlp"
    except:
        dl_method = "ffmpeg"
from datetime import datetime

config = {
    'default_dir': '',
    'always_verbose': False,
    'always_m3u8': False,
    'always_replies': False,
    'quit_on_json': True,
}

# TODO: images, # of quotes in chain, subtitles
# TODO: dl_method options, probably make it a dictionary

def help_text():
    sys.exit("""
bsky-dl [url] [path] [options]

Download videos and extract json from Bluesky posts.

OPTIONS:
    --m3u8: download m3u8 video rather than blob
    --json: print the getPostThread JSON to file
    --replies: include replies and parents in JSON
    --verbose: print additional logging messages to terminal

The file download path uses the following hierarchy:
    1. Path specified in command
    2. default_dir specified in script
    3. Current working directory

The following hierachy is used for m3u8 downloads, depending on availability:
    1. streamlink (pip install streamlink)
    2. yt-dlp (pip install yt-dlp)
    3. ffmpeg (native package)
    """)

def input_validation(filename):
    if "--help" in sys.argv: help_text()
    m3u8_mode = 0 if ("--m3u8" not in sys.argv and config['always_m3u8'] != True) else (sys.argv.remove("--m3u8") or 1)
    json_mode = 0 if "--json" not in sys.argv else (sys.argv.remove("--json") or 1)
    reply_mode = 0 if ("--replies" not in sys.argv and config['always_replies'] != True) else (sys.argv.remove("--replies") or 1)
    verbose = 0 if ("--verbose" not in sys.argv and config["always_verbose"] != True) else (sys.argv.remove("--verbose") or 1)
    url = sys.argv[1] if len(sys.argv) >= 2 else sys.exit("No url entered.")
    directory = sys.argv[2] if len(sys.argv) >= 3 else (Path.cwd() if config["default_dir"] == '' else config["default_dir"])
    if not Path(directory).is_dir():
        if Path(directory).parent.is_dir(): sys.exit(f"{directory} is not a valid directory")
        directory = str(input_path.parent)
        filename = input_path.stem
    return url, directory, filename, json_mode, m3u8_mode, reply_mode, verbose

def url2uri(post_url):
    parts = post_url.rstrip('/').split('/')
    if len(parts) < 4: raise ValueError(f"Post URL '{post_url}' does not have enough segments.")
    rkey, username = parts[-1], parts[-3]
    # return f"at://{resolve_did(username)}/app.bsky.feed.post/{rkey}", rkey
    return f"at://{username}/app.bsky.feed.post/{rkey}", rkey

def resolve_did(handle):
    if handle.startswith("did:"): return handle 
    response = requests.get(f'https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle={handle}')
    if response.status_code != 200: raise Exception(f"Failed to resolve DID: '{response.text}'")
    return response.json()['did']

def get_post_thread(post_url, reply_mode):
    at_uri, rkey = url2uri(post_url)
    params = {'uri': at_uri, 'depth': 1000 if reply_mode else 0, 'parentHeight': 1000 if reply_mode else 0}
    response = requests.get('https://public.api.bsky.app/xrpc/app.bsky.feed.getPostThread', headers={'Content-Type': 'application/json'}, params=params)
    # response = requests.get('https://public.api.bsky.app/xrpc/app.bsky.feed.getQuotes', headers={'Content-Type': 'application/json'}, params={'uri': at_uri, 'limit': 100})
    if response.status_code != 200: raise Exception(f"Failed to retrieve post thread: '{response.text}'")
    return response.json(), rkey

def check_ffmpeg(verbose):
    if verbose: print("streamlink is not installed. Checking for ffmpeg.")
    try:
        if subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).returncode:
            sys.exit("ffmpeg is not installed.")
        elif verbose: print("ffmpeg is installed. Downloading file...")
    except FileNotFoundError: sys.exit("ffmpeg is not installed.")

def download_video(post_data, path, m3u8_mode, verbose):
    if not post_data.get('thread', {}).get('post', {}).get('record', {}).get('embed', {}).get('video', ''): sys.exit("This post has no video.")
    if m3u8_mode:
        if not (m3u8_url := post_data.get('thread', {}).get('post', {}).get('embed', {}).get('playlist', '')): sys.exit(f"Post does not have a video embed.")
        if dl_method == "streamlink":
            if not (best_stream := streamlink.streams(m3u8_url).get('best')): sys.exit('No m3u8 streams found.')
            with open(path, 'wb') as f, best_stream.open() as stream: 
                while (data := stream.read(1024)): f.write(data)
        elif dl_method == "yt-dlp":
            try: yt_dlp.YoutubeDL({'format': 'best', 'outtmpl': path, 'quiet': False if verbose else True}).download([m3u8_url])
            except Exception as e: sys.exit(f"Error downloading m3u8 stream: {str(e)}")
        elif dl_method == "ffmpeg": 
            check_ffmpeg(verbose)
            response = subprocess.run(['ffmpeg', '-i', m3u8_url, '-c', 'copy', '-bsf:a', 'aac_adtstoasc', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if response.returncode != 0: sys.exit(f"ffmpeg download to {path} failed.")
        print(f"Video from m3u8 segments successfully downloaded to {path} with {dl_method}")
    else:
        did = post_data.get('thread', {}).get('post', {}).get('author', {}).get('did', {})
        blob_cid = post_data.get('thread', {}).get('post', {}).get('record', {}).get('embed', {}).get('video', {}).get('ref', {}).get('$link', "")
        response = requests.get(f"https://bsky.social/xrpc/com.atproto.sync.getBlob?did={did}&cid={blob_cid}")
        if response.status_code != 200: sys.exit(f"Failed to download blob: '{response.text}'")
        if 'video' not in response.headers.get('Content-Type', ''): sys.exit("Response is not a valid video file.")
        with open(path, 'wb') as f: f.write(response.content)
        print(f"Blob successfully downloaded to {path}")

def main():
    post_url, directory, filename, json_mode, m3u8_mode, reply_mode, verbose = input_validation("")
    post_data, rkey = get_post_thread(post_url, reply_mode)
    filename = f"{directory}/{rkey}" if filename == "" else f"{directory}/{filename}"
    # if json_mode:
    #     index_time = post_data.get('thread').get('post').get('indexedAt')
    #     print(f'indexedAt: {datetime.fromisoformat(index_time.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")}')
    #     post_time = post_data.get('thread').get('post').get('record').get('createdAt')
    #     print(f'createdAt: {datetime.fromisoformat(post_time.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")}')
    # exit()
    if json_mode: (json.dump(post_data, open(f'{filename}.json', 'w'), indent=4), print(f"JSON extracted to '{filename}.json'"), sys.exit() if config['quit_on_json'] else None)
    download_video(post_data, f'{filename}.mp4', m3u8_mode, verbose)

if __name__ == "__main__":
    main()
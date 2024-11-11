#!/usr/bin/env python

from bsky_api import get_post_thread, validate_path, save_json, print_json, url_basename
import sys
from pathlib import Path

def help_text():
    sys.exit("""
bsky-dl [url] [path] [options]

Extract JSON from Bluesky posts.

OPTIONS:
    --replies: include replies and parents in JSON
    --silent: prevent printing JSON to screen
    --print: prevent saving JSON to file

The file download path uses the following hierarchy:
    1. Path specified in command
    2. default_dir specified in script
    3. Current working directory
    """)

def input_validation():

    config = {
        'default_dir': '',
        'always_replies': False,
        'always_print': False,
        'always_silent': True,
    }

    if "--help" in sys.argv: help_text()

    def validate_mode(option):
        flag = f"--{option}"
        config_key = f"always_{option}"

        if flag not in sys.argv:
            if not config.get(config_key, False):
                return 0
        else:
            sys.argv.remove(flag)
        return 1

    reply_mode, silent_mode, print_mode = validate_mode("replies"), validate_mode("silent"), validate_mode("print")
    url = sys.argv[1] if len(sys.argv) >= 2 else sys.exit("No url entered.")
    path = sys.argv[2] if len(sys.argv) >= 3 else (Path.cwd() if not config["default_dir"] else config["default_dir"])
    return url, path, reply_mode, silent_mode, print_mode

def main():
    url, path, reply_mode, silent_mode, print_mode = input_validation()

    depth = 1000 if reply_mode else 0
    parent_height = 1000 if reply_mode else 0

    thread = get_post_thread(url, depth, parent_height)

    if not silent_mode:
        print_json(thread)
    if print_mode:
        return

    rkey = url_basename(url)
    path = validate_path(path, rkey, ['json'])
    save_json(thread, path)

if __name__ == "__main__":
    main()
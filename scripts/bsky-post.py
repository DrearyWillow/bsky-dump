#!/usr/bin/env python

from bsky_api import *
import sys

def validate_inputs():
    config = {
        'username': "",
        'password': "",
        'text_prompt': True,
        'blob_prompt': False,
        'alt_text': False,
    }

    if "--auth" in sys.argv:
        idx = sys.argv.index("--auth")
        if len(sys.argv) < idx + 2:
            username, password = None, None
            sys.argv = sys.argv[:idx]
        else:
            username, password = sys.argv[idx + 1], sys.argv[idx + 2]
            sys.argv.remove(username)
            sys.argv.remove(password)
            # sys.argv.pop(idx + 1)
            # sys.argv.pop(idx + 2)
        sys.argv.remove("--auth")
    else:
        username = config['username']
        password = config['password']

    if "--parent" in sys.argv:
        idx = sys.argv.index("--parent")
        if len(sys.argv) < idx + 1:
            parent_url = None
        else:
            parent_url = sys.argv[idx + 1]
            sys.argv.remove(parent_url)
        sys.argv.remove("--parent")
    else:
        parent_url = None
    # parent_url = sys.argv[2] if len(sys.argv) >= 3 else None

    # set these inputs to 0 if we don't want to be prompted
    text = None
    blob_path = None
    alt_text = None
    if not config['blob_prompt']:
        blob_path = 0
    if not config['blob_prompt']:
        alt_text = 0

    return username, password, text, parent_url, blob_path, alt_text

def main():
    create_post_prompt(**validate_inputs())

if __name__ == "__main__":
    main()
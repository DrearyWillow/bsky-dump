
from bsky_utils import *
import os
from dotenv import load_dotenv

def construct_like_record(uri):
    did, nsid, rkey = decompose_uri(uri)
    cid = (get_record(did, nsid, rkey)).get('cid')
    # service_endpoint = get_service_endpoint(did)
    # cid = requests.get(f"{service_endpoint}/xrpc/com.atproto.repo.getRecord?repo={did}&collection={nsid}&rkey={rkey}").json().get('cid')
    record = {
        "$type": "app.bsky.feed.like",
        "subject": {
            "cid": cid,
            "uri": uri
        },
        "createdAt": generate_timestamp()
    }
    return record

if __name__ == "__main__":

    load_dotenv()
    # print(os.getenv("BSKY_UNAME"), os.getenv("BSKY_PW"))
    did = resolve_handle(os.getenv("BSKY_UNAME"))
    service = get_service_endpoint(did)
    session = get_session(os.getenv("BSKY_UNAME"), os.getenv("BSKY_PW"), service)

    uri = input("AT-URI: ")
    record = construct_like_record(uri)

    create_record(session, service, record)
    


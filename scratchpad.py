from bsky_utils import *
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    print(os.getenv("BSKY_UNAME"), os.getenv("BSKY_PW"))
    print(resolve_handle(os.getenv("BSKY_UNAME")))
    # did, nsid, rkey = decompose_uri(input("AT-URI: "))
    # service = get_service_endpoint(did)
    # session = get_session(os.getenv("BSKY_UNAME"), os.getenv("BSKY_PW"), service)
    # delete_record(session, service, nsid, rkey)
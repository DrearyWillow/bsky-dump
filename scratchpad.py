from bsky_utils import *
from secret import login

if __name__ == "__main__":
    did, nsid, rkey = decompose_uri(input("AT-URI: "))
    service = get_service_endpoint(did)
    session = get_session(login['uname'], login['pw'], service)
    delete_record(session, service, nsid, rkey)
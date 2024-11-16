from bsky_utils import *
from secret import creds

handle = "dreary.dev"
did = resolve_handle(handle)
endpoint = get_service_endpoint(did)
session = get_session(creds["uname"], creds["pw"], endpoint)

params = {'limit': 100}
token = session.get('accessJwt')
headers = {'Authorization': f'Bearer {token}'}
api = f"{endpoint}/xrpc/app.bsky.graph.getMutes"

mutes = safe_request('get', api, headers=headers, params=params)

print_json(mutes)

from bsky_utils import *

did = 'did:plc:hx53snho72xoj7zqt5uice4u'
endpoint = get_service_endpoint(did)
session = get_session(did, 'PASSWORD', endpoint)

url = f"{endpoint}/xrpc/com.atproto.repo.createRecord"
token = session.get('accessJwt')
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {token}'
}

followers = get_followers_return(did)

for follower in followers:
    follower = follower.get('did')
    print(follower)
    payload = json.dumps({
        "repo": 'did:plc:hx53snho72xoj7zqt5uice4u',
        "collection": "app.bsky.graph.listitem",
        "validate": True,
        "record": {
            "list": "at://did:plc:hx53snho72xoj7zqt5uice4u/app.bsky.graph.list/3ldc5ohwfsu2n",
            "$type": "app.bsky.graph.listitem",
            "subject": follower,
            "createdAt": "2024-12-14T15:00:00.000Z"
        }
    })
    safe_request('post', url, headers=headers, data=payload)

print("Done: https://bsky.app/profile/did:plc:hx53snho72xoj7zqt5uice4u/lists/3ldc5ohwfsu2n")
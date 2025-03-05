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

payload = json.dumps({
    "repo": 'did:plc:hx53snho72xoj7zqt5uice4u',
    "collection": "app.bsky.feed.like",
    "validate": True,
    "record": {
        "$type": "app.bsky.feed.like",
        "subject": {
            "cid": "bafyreiel6lmtdc2xcwsogrjbwjduns2yqqxgngnwftbwxbnhlvsfpnttyu",
            "uri": "at://did:plc:xoktq5heiz7qsjrpz4mcckum/app.bsky.feed.like/3leajufiwyq2t"
        },
        "createdAt": "2024-12-26T22:34:57.498Z"
    }
})
safe_request('post', url, headers=headers, data=payload)

print("done. i love you ollie.")
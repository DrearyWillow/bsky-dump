import requests
import json

credentials = {
    'username': "",
    'password': ""
}

def get_session():
    url = 'https://bsky.social/xrpc/com.atproto.server.createSession'

    payload = {
        'identifier': credentials["username"],
        'password': credentials["password"]
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get access token. Status code: {response.status_code}. Response: {response.text}")
        

did = "did:plc:znmktqkgqhm2twxcbqiszvx4"

rkey = "3l5mamlis3w2s"
now = "2024-10-03T12:25:07.166Z"
text = "swag"

post = {
    "$type": "app.bsky.feed.post",
    "text": text,
    "createdAt": now,
    "langs": [
        "en"
    ],
    "reply": {
        "parent": {
            "cid": "bafyreicw4c2i3f66bv5hqr7yfdrvvwmoymn2up6uxmb2tvxejxdoc23tne",
            "uri": "at://did:plc:znmktqkgqhm2twxcbqiszvx4/app.bsky.feed.post/3l5mameytpr2m"
        },
        "root": {
            "cid": "bafyreicw4c2i3f66bv5hqr7yfdrvvwmoymn2up6uxmb2tvxejxdoc23tne",
            "uri": "at://did:plc:znmktqkgqhm2twxcbqiszvx4/app.bsky.feed.post/3l5mameytpr2m"
        }
    },
}

session = get_session()

service_endpoint = "https://magic.us-west.host.bsky.network"
# did = session.get('did')
# service_endpoint = get_service_endpoint(did)
url = f"{service_endpoint}/xrpc/com.atproto.repo.createRecord"


payload = json.dumps({
"repo": did,
"collection": "app.bsky.feed.post",
"validate": True,
"rkey": rkey,
"record": post,
})

headers = {
'Content-Type': 'application/json',
'Accept': 'application/json',
'Authorization': f'Bearer {session.get('accessJwt')}'
}

response = requests.post(url, headers=headers, data=payload)

if response.status_code == 200:
    rkey = response.json().get('uri').rstrip('/').split('/')[-1]
    print(f"Post created successfully: https://bsky.app/profile/{session.get('handle')}/post/{rkey}")
else:
    raise Exception(f"Failed to create post. Status code: {response.status_code}. Response: {response.text}")

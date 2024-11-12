
from bsky_utils import *

# BOOLS ARE NOT BOOLS

service = "https://shiitake.us-east.host.bsky.network"
lexicon = "com.atproto.repo.listRecords"
did = "did:plc:tj7g244gl5v6ai6cm4f4wlqp"
nsid = "app.bsky.feed.post"
limit = 2
cursor = None
reverse = "true"


params = {
    "repo": did,
    "collection": nsid,
    "limit": limit,
    "cursor": cursor,
    "reverse": reverse,
}

api = f"{service}/xrpc/{lexicon}"
res = safe_request("get", api, params=params).get('records')
for r in res:
    print(r.get("uri"))
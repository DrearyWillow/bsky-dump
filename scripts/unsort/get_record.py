from bsky_utils import *

# uri = "at://did:plc:xoktq5heiz7qsjrpz4mcckum/app.bsky.feed.like/3lj4shf4en42c"
uri = input("AT-URI: ")
did, nsid, rkey = decompose_uri(uri)
print_json(get_record(did, nsid, rkey))

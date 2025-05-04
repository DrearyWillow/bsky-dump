from bsky_utils import *


# did = "did:plc:wbxlr7nn6circzbjz4rootar"
# service = get_service_endpoint(did)

# likes = list_records(did, service, "app.bsky.feed.like")

# save_json(likes)


import json
with open('./output.json', "r") as file:
    likes = json.load(file)

print(len(likes))
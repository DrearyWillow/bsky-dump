from bsky_utils import *

lists = get_lists(resolve_handle("dreary.dev")).get("lists")
# lists = safe_request("get", "https://public.api.bsky.app/xrpc/app.bsky.graph.getLists?actor=did:plc:hx53snho72xoj7zqt5uice4u")

for listr in lists:
    print(listr.get('name'))
    items = get_list_items(listr.get("uri"))
    for item in items:
        did = item.get("subject").get("did")
        handle = item.get("subject").get("handle")
        # handle = get_did_doc(subject).get("alsoKnownAs")[0].replace("at://")
        print(f"\"{did}\", // @{handle}")
    print(f"\n\n")
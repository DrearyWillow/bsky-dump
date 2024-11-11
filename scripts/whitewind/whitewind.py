from bsky_utils import *
import re
import sys


def list_records(did, service, nsid, limit, cursor):
    params = {
        "repo": did,
        "collection": nsid,
        "limit": limit,
        "cursor": cursor,
    }
    api = f"{service}/xrpc/com.atproto.repo.listRecords"
    return safe_request("get", api, params=params)


def ww_title2uri(did, service, title):
    nsid = "com.whtwnd.blog.entry"
    limit = 100
    cursor = None
    title = title.replace("%20", " ")

    while True:
        data = list_records(did, service, nsid, limit, cursor)
        if (records := data.get("records")) and (len(records) > 0):
            for idx, record in enumerate(records):
                if record.get("value").get("title") == title:
                    return record.get("uri")
        else:
            break
        if not (cursor := data.get("cursor")):
            break
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Enter a White Wind URL")
    url = sys.argv[1]
    whtwind_pattern = r"^https:\/\/whtwnd\.com\/(?P<handle>[\w.:%-]+)\/(?:entries\/(?P<title>[\w.:%-]+)(?:\?rkey=(?P<rkey>[\w.:%-]+))?|(?P<postId>[\w.:%-]+))$"
    match = re.match(whtwind_pattern, url)
    handle, title, rkey, rkey2 = match.groups()
    lexicon = "com.whtwnd.blog.entry"
    did = resolve_handle(handle)
    if not did:
        sys.exit("Invalid DID")
    if rkey or rkey2:
        uri = f"at://{did}/{lexicon}/{rkey or rkey2}"
    elif title:
        service = get_service_endpoint(did)
        uri = ww_title2uri(did, service, title)
        if not uri:
            sys.exit(f"No blog with title '{title}' found for {did}")
    else:
        sys.exit(f"No com.whtwnd.blog.entry identifier for post from {did}")

    print(f"{linkify(uri, uri.replace("at://", "https://pdsls.dev/at/"))}")


from bsky_utils import *
from dotenv import load_dotenv
import os

# oauth lmao
# create pin with same createdAt as post option -- oh wait nan doesn't use createdAt
# async / yield? but i wanna applywrites

# prevent dupe option

# choose from existing pinboard
# create new pinboard

# alternative string (could be emoji or whatever else)
# pin posts themselves, parent, or root

# search query
# gather all records fallback

# python sys argv manager?

def credentials(validate_handle=False):
    load_dotenv()
    if not (handle := os.getenv("HANDLE")) or not (password := os.getenv("PASSWORD")):
        raise Exception("Credentials ('HANDLE' and 'PASSWORD') not defined in .env")
    if not (did := resolve_handle(handle)):
        raise Exception("Unable to resolve handle.")
    if not (service := get_service_endpoint(did)):
        raise Exception("Unable to retrieve service endpoint.")
    if not (session := get_session(did, password, service)):
        raise Exception("Invalid credentials.")
    if validate_handle and handle.startswith("did:"):
        handle = retrieve_handle(handle)
    return handle, did, session, service


def search_posts(q, author, session=None, service=None):
    # {service}/xrpc/app.bsky.feed.getFeed?feed=at://did:plc:q6gjnaw2blty4crticxkmujt/app.bsky.feed.generator/my-pins&limit=100
    # public api broken rn
    service = service or "https://public.api.bsky.app"
    url = f"{service}/xrpc/app.bsky.feed.searchPosts"
    params = {
        "q": q,
        "sort": "latest",
        "author": author,
        "limit": 100
    }
    if session:
        token = session.get('accessJwt')
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }
    else:
        headers = None
    # return safe_request('get', url, headers=headers, params=params)
    return generic_page_loop_return(url, params, ['posts'], ['cursor'], headers=headers)
    # while True:
    #     res = safe_request('get', url, params=params) or {}
    #     posts = res.get('posts', [])
    #     yield from posts

    #     cursor = res.get('cursor')
    #     if not cursor:
    #         break
    #     params['cursor'] = cursor

def select_pinboard(session, service):
    # no options yet
    record = {
        '$type': 'xyz.jeroba.tags.tag',
        'title': '📌'
    }
    return create_record(session, service, record['$type'], record)

def main():
    handle, did, session, service = credentials()

    _, _, pinboard_rkey = decompose_uri(select_pinboard(session, service))

    posts = search_posts('📌', did, session=session, service=service)
    # print_json(posts)
    
    uri_mode = None
    match uri_mode:
        case 'root':
            path = ['record', 'reply', 'root', 'uri']
        case 'self':
            path = ['uri']
        case _:
            path = ['record', 'reply', 'parent', 'uri']

    # path = {
    #     'root': ['record', 'reply', 'root', 'uri'],
    #     'self': ['uri'],
    # }.get(uri_mode, ['record', 'reply', 'parent', 'uri'])

    records = [{
        'tag': pinboard_rkey,
        '$type': 'xyz.jeroba.tags.tagged',
        'record': uri
    } for uri in traverse(posts, path, get_all=True)]

    apply_writes_batch(session, service, records)
    print('Writes complete.')

    # uris = [uri for post in posts if (uri := post.get('uri'))]
    # for post in posts:
    #     uri = post.get('uri')
    #     parent = traverse(post, ['record', 'reply', 'parent', 'uri'])
    #     root = traverse(post, ['record', 'reply', 'root', 'uri'])
    #     created_at = traverse(post, ['record', 'reply', 'createdAt'])


if __name__ == "__main__":
    main()

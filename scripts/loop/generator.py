
from bsky_api import *

def get_followers(actor):
    api = f"https://public.api.bsky.app/xrpc/app.bsky.graph.getFollowers"
    page_limit = 100
    params = {"actor": actor, 'limit': page_limit}

    res = requests.get(api, params=params).json()
    output = res['followers']

    yield from output

    while cursor := res.get('cursor'):
        param_copy = params
        param_copy['cursor'] = cursor
        res = requests.get(api, params=param_copy).json()
        followers = res['followers']
        yield from followers

count = 0
seen_ids = set()
followers = get_followers('did:plc:355lbopbpckczt672hss2ra4')
for follower in followers:
    fdid = follower.get('did')
    if fdid not in seen_ids:
        seen_ids.add(fdid)
    else:
        print(f"DUPE {fdid}")
    count += 1
print(f"Total: {count}")


# def fetch_page(api, params, cursor=None):
#     params['cursor'] = cursor
#     data = safe_request('get', api, params=params)
#     # save_json(data, prompt=True)
#     return data

# def generic_page_loop(api, page_limit, path_to_output, path_to_cursor, **kwargs):
#     # TODO: try out yield maybe?
#     params = {**kwargs, 'limit': page_limit}

#     res = fetch_page(api, params)
#     output = traverse(res, path_to_output)

#     # not super reliable `and` condition because sometimes there are deactivated records
#     # so i'm just relying on cursor being None
#     # while traverse(res, path_to_cursor): #and (len(traverse(res, path_to_output)) >= page_limit):
#     #     res = fetch_page(api, params, traverse(res, path_to_cursor))
#     #     output.extend(traverse(res, path_to_output))
#     # return output

#     yield from output

#     while cursor := traverse(res, path_to_cursor): #and (len(traverse(res, path_to_output)) >= page_limit):
#         res = traverse(fetch_page(api, params, cursor), path_to_output)
#         yield from res

# def get_followers(actor):
#     api = f"https://public.api.bsky.app/xrpc/app.bsky.graph.getFollowers"
#     params = {"actor": actor}
#     return generic_page_loop(api, 100, ['followers'], ['cursor'], **params)
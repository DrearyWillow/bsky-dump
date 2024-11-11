from bsky_api import *
import sys

handle = 'alt.bun.how'
did = resolve_did(handle)
print(did)
# url = f'https://resolver.identity.foundation/1.0/identifiers/{did}'
url = f'https://plc.directory/{did}'
response = requests.get(url)
print_json(response.json())



# handle = 'alt.bun.how'
# r = safe_request('get', f'https://public.api.bsky.app/xrpc/com.atproto.identity.resolveHandle?handle={handle}')
# print(r)

# url = sys.argv[1]
# # uri = url2uri(url)
# did, collection, rkey = decompose_url(url)
# service_endpoint = resolve_service_endpoint(did)
# data = get_post_thread(url)
# blob_cid = traverse(data, ['post', 'record', 'embed', 'video', 'ref', '$link'])

# print(f"did: {did}")
# print(f"blob cid: {blob_cid}")
# print(f"service endpoint: {service_endpoint}")
# blob_url = f"{service_endpoint}/xrpc/com.atproto.sync.getBlob?did={did}&cid={blob_cid}"
# print(f"blob_url: {blob_url}")

# response = requests.get(blob_url)
# if response.status_code != 200: sys.exit(f"Failed to download blob: '{response.text}'")

# path = "/home/kyler/Downloads/test.mp4"
# with open(path, 'wb') as f: f.write(response.content)
# print(f"Blob successfully downloaded to {path}")


# print(resolve_did('dreary.bsky.social'))

# response = safe_request('get',
#     'https://public.api.bsky.app/xrpc/app.bsky.feed.getPostThread',
#     headers={'Content-Type': 'application/json'},
#     params={
#         'uri': uri,
#     })

# endpoint = 'https://b481a144-23e5-4fa9-83ae-e448d3593655.whtwnd.com'
# uri = 'at://did:plc:oisofpd7lj26yvgiivf3lxsi/com.whtwnd.blog.entry/3kpqdnwwbbs2i'
# response = safe_request('get',
#     f'{endpoint}/xrpc/com.whtwnd.blog.entry',
#     headers={'Content-Type': 'application/json'},
#     params={
#         'uri': uri,
#     })

# url = 'https://b481a144-23e5-4fa9-83ae-e448d3593655.whtwnd.com/xrpc/com.whtwnd.blog.getMentionsByEntry?postUri=at%3A%2F%2Fdid%3Aplc%3Aoisofpd7lj26yvgiivf3lxsi%2Fcom.whtwnd.blog.entry%2F3kpqdnwwbbs2i'
# url = 'https://b481a144-23e5-4fa9-83ae-e448d3593655.whtwnd.com/xrpc/com.whtwnd.blog.entry?postUri=at%3A%2F%2Fdid%3Aplc%3Aoisofpd7lj26yvgiivf3lxsi%2Fcom.whtwnd.blog.entry%2F3kpqdnwwbbs2i'

# response = safe_request('get', url)

# print_json(response)

# thread = get_post_thread('https://bsky.app/profile/pet.bun.how/post/3l7wbh7ouvq2i')
# output = traverse(thread, ['post', 'likeCount'], ['post', 'repostCount'], ['post', 'record', 'createdAt'], get_all=True)
# print(output)
from bsky_utils import *

def generic_page_loop_return(api, params, path_to_output, path_to_cursor):
    res = safe_request('get', api, params=params)
    output = traverse(res, path_to_output)
    while cursor := traverse(res, path_to_cursor):
        res = safe_request('get', api, params={**params, 'cursor': cursor})
        output.extend(traverse(res, path_to_output))
    return output

def process_posts(did, service, nsid):
    api = f'{service}/xrpc/com.atproto.repo.listRecords'
    params = {
        'repo': did,
        'collection': nsid,
        'limit': 100,
    }
    return generic_page_loop_return(api, params, ['records'], ['cursor'])

user_handle = input("Handle: ")
if not user_handle:
    return
user_did = resolve_handle(user_handle)
if not user_did:
    return
service = get_service_endpoint(user_did)
if not service:
    return
posts = process_posts(user_did, service, "app.bsky.feed.post")
if not posts:
    print("No quote posts found")
    return

self_quotes = 0
total_quotes = 0
quote_counts = {}

save_json(posts)

for post in posts:
    embed = post.get('value', {}).get('embed', {})
    if not embed or 'record' not in embed:
        continue
    
    record = embed['record'].get('record') or embed['record']
    uri = record.get('uri', '')

    if not uri:
        continue

    did, _, _ = decompose_uri(uri)

    if not did:
        continue
        
    if did == user_did:
        self_quotes += 1

    quote_counts[did] = quote_counts.get(did, 0) + 1
    total_quotes += 1

# sort quotes by count (highest first)
sorted_quotes = sorted(quote_counts.items(), key=lambda x: x[1], reverse=True)

# print and save to file
output_lines = ["DID\tQuotes\tHandle"]
for did, count in sorted_quotes:
    handle = retrieve_handle(did)
    if not handle:
        handle = "🪦"
    output_lines.append(f"{did}\t{count}\t{handle}")

output_text = "\n".join(output_lines)
print(output_text)

with open("quote_counts.txt", "w") as f:
    f.write(output_text)

# print summary
print(f"Total Posts: {len(posts)}")
print(f"Total Quotes: {total_quotes}")
print(f"Self Quotes: {self_quotes} ({(self_quotes/total_quotes*100):.2f}%)" if total_quotes else "Self Quotes: 0 (0%)")



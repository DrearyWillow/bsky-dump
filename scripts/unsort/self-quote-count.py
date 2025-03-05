from bsky_utils import *

user_did = resolve_handle("cwonus.org")
service = get_service_endpoint(user_did)
posts = list_records(user_did, service, "app.bsky.feed.post")

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



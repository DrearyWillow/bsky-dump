from bsky_utils import *
import webbrowser

# api = 'https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed'
# params = {
#     'actor': 'alice-roberts.bsky.social',
#     'limit': 100,
#     'filter': 'posts_with_media',
#     'includePins': False
# }
# posts = generic_page_loop_return(api, params, ['feed'], ['cursor'])

# save_json(posts)

file_path = "/home/kyler/Code/bsky/bsky-dump/output.json"
with open(file_path, 'r') as file:
    posts = json.load(file)

vid_posts = []
for post in posts:
    if (media_type := traverse(post, ['post', 'embed', '$type'])) == "app.bsky.embed.images#view":
        continue
    if media_type == 'app.bsky.embed.recordWithMedia#view':
        media_type = traverse(post, ['post', 'embed', 'media', '$type'])
        if media_type == "app.bsky.embed.images#view":
            continue
    vid_posts.append(post)
    url = f"https://pdsls.dev/at/{traverse(post, ['post', 'uri']).replace('at://', '')}"
    webbrowser.open_new_tab(url)
    print(url)

save_json(vid_posts, "/home/kyler/Code/bsky/bsky-dump/vids.json")




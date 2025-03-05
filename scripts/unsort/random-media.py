from bsky_utils import *
import random

api = 'https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed'
params = {
    'actor': 'dreary.dev',
    'limit': 100,
    'filter': 'posts_with_media',
    'includePins': False
}
posts = generic_page_loop_return(api, params, ['feed'], ['cursor'])

save_json(posts)

selected = random.choice(posts)

print(selected.get('post').get('embed').get('images')[0].get('fullsize'))

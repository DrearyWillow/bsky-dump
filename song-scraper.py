from bsky_utils import *

handles = [
    'dreary.dev',
    # 'drearydev.bsky.social',
    # 'renahlee.bsky.social',
    'mary.my.id',
    'renahlee.com',
    # 'pet.bun.how'
]

Path("media").mkdir(parents=True, exist_ok=True)

print()

for handle in handles:
    print(f'Attempting: {handle}')
    Path(f"media/{handle}").mkdir(parents=True, exist_ok=True)

    # path = f'/home/kyler/Code/bsky/bsky-dump/posts/{handle}-posts.json'
    path = f'media/{handle}/posts.json'
    if not Path(path).is_file():
        # from:handle domain:hostname doesn't work if it's just an embed
        # also theoretically i could check video/image alt text but
        # no one does that but me, and i'd have to parse it. ugly
        did = resolve_handle(handle)
        if not did:
            print("invalid did")
            continue
        service = get_service_endpoint(did)
        if not service:
            print("invalid service")
            continue
        posts = list_records(did, service, 'app.bsky.feed.post')
        save_json(posts, path)
        print("Posts retrieved")
    else:
        with open(path, "r", encoding="utf-8") as file:
            posts = json.load(file)
        print("JSON retrieved")

    uri_list = set()
    yt, sc, bc, sp = set(), set(), set(), set()

    for post in posts:
        uris = traverse2(
            post,
            ['value', 'embed', 'external', 'uri'],
            ['value', 'facets', 'features', 'uri'],
            get_all=True
        )
        if not uris:
            continue
        for uri in uris:
            # i want to report on them separately
            # if any(substring in uri.split('/')[2] for substring in ['youtu', 'bandcamp', 'soundcloud', 'spotify']):
            #     uri_list.add(uri)
            hostname = uri.split('/')[2]
            if 'youtu' in hostname:
                yt.add(uri)
                uri_list.add(uri)
            elif 'soundcloud' in hostname:
                sc.add(uri)
                uri_list.add(uri)
            elif 'bandcamp' in hostname:
                bc.add(uri)
                uri_list.add(uri)
            elif 'spotify' in hostname:
                sp.add(uri)
                uri_list.add(uri)

    print(f'Media search complete: {handle}')

    # path = f'/home/kyler/Code/bsky/bsky-dump/posts/{handle}-linkdump.txt'
    path = f'media/{handle}/linkdump.txt'
    with open(path, "w", encoding="utf-8") as file:
        file.writelines(f"{uri}\n" for uri in sorted(uri_list))
    
    obj = {
        'youtube': sorted(yt),
        'soundcloud': sorted(sc),
        'bandcamp': sorted(bc),
        'spotify': sorted(sp)
    }
    path = f'media/{handle}/links.json'
    save_json(obj, path)

    print(f"Results: {len(uri_list)} total, {len(yt)} youtube, {len(sc)} soundcloud, {len(bc)} bandcamp, {len(sp)} spotify")
    print()

# for handle in handles:
#     path = f'/home/kyler/Code/bsky/bsky-dump/posts/{handle}-posts.json'
#     with open(path, "r", encoding="utf-8") as file:
#         posts = json(file)
    
#     path = f'/home/kyler/Code/bsky/bsky-dump/posts/{handle}-links.txt'
#     with open(path, "w", encoding="utf-8") as file:

#         for post in posts:
#             uris = traverse2(
#                 post,
#                 ['value', 'embed', 'external', 'uri'],
#                 ['value', 'facets', 'features', 'uri'],
#                 get_all=True
#             )
#             if not uris:
#                 continue
#             for uri in uris:
#                 if any(substring in uri.split('/')[2] for substring in ['youtu', 'bandcamp', 'soundcloud', 'spotify']):
#                     file.write(uri + "\n")

#     print(f'Media search complete: {handle}')
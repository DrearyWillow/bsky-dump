from bsky_api import *
import sys

# session = get_session('', '')

# create_post_prompt('', '', parent_url=0, blob_path=0, alt_text=0)



# endpoint = retrieve_service_endpoint(did)
# for follow in generic_get_follows(did, endpoint):
#     print_json(follow)

# did = retrieve_did('alice-roberts.bsky.social')
did = retrieve_did('kasey.cafe')

# print_json(get_profile(did))
# exit()
count, ecount = 0, 0
flist = {}
flist['followers'] = []
followers = get_followers(did)
for follower in followers:
    flist['followers'].append({**follower})

    # fdid = follower['did']
    # fhandle = follower['handle']
    # flist[fdid] = fhandle

    # try:
    #     get_profile(fdid)
    #     flist.extend([{'did': fdid, 'handle': fhandle, 'status': "active"}])
    # except Exception as e:
    #     message = str(e)
    #     if "not found" in message:
    #         status = "not found"
    #     elif "deactivated" in message:
    #         status = "deactivated"
    #     elif "suspended" in message:
    #         status = "suspended"
    #     else:
    #         status = "unknown"
    #     flist.extend([{'did': fdid, 'handle': fhandle, 'status': status}])
    #     ecount += 1
    count += 1
print(f"Total: {count}")
# print(f"Error Count: {ecount}")
save_json(flist)



# uri = 'https://bsky.app/profile/alice-roberts.bsky.social/post/3l4vhpnjilh2v'

# count = 0
# # quotes = get_post_quotes(uri)
# # print_json(quotes)
# for quote in get_post_quotes(uri):
#     print(quote['author']['handle'])
#     count += 1
# print(count)

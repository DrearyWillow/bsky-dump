from bsky_utils import *
from secret import creds


handle = "dreary.dev"


# save_json(follows_since)
# exit()

sel = cli_list_menu(handle)

# save_json(get_list(sel.get('uri')))
# exit()

items = get_list_items(sel.get('uri'))

# for item in items:
    
list_users = [item.get('subject').get('did') for item in items]

# save_json(items)


did = resolve_handle(handle)
timestamp = "2024-10-31T12:17:02.787509Z" #can get from list description, or maybe the createdAt of the last user in the list?
endpoint = get_service_endpoint(did)

follows_since = get_follows_since(did, endpoint, timestamp)



session = get_session(creds.get('uname'), creds.get('pw'), endpoint)

no_act = input("Print mode?") #proof of concept
no_act = True

for follow in follows_since:
    if follow not in list_users:
        print(follow)
        if not no_act: #proof of concept
            add_user_to_list(session, endpoint, sel, follow)





from bsky_utils import *
from secret import creds

handle = "dreary.dev"

print("select list to add to:")

mainlist = cli_list_menu(handle)

endpoint = get_service_endpoint(resolve_handle(handle))

session = get_session(creds['uname'], creds['pw'], endpoint)



addlist = cli_list_menu(handle)

items = get_list_items(addlist.get('uri'))

# newlist = create_list(session, endpoint, name="compiled meow")

for item in items:
    add_user_to_list(session, endpoint, mainlist, item.get('subject').get('did'))

# save_json(items)
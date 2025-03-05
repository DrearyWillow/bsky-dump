
from bsky_utils import *

uris = ["at://did:plc:hx53snho72xoj7zqt5uice4u/app.bsky.graph.list/3kivqnnhzcr27",
    "at://did:plc:hx53snho72xoj7zqt5uice4u/app.bsky.graph.list/3ksbhekrfpk2n",
    "at://did:plc:hx53snho72xoj7zqt5uice4u/app.bsky.graph.list/3kwpjne65r223"
    # "at://did:plc:hx53snho72xoj7zqt5uice4u/app.bsky.graph.list/3lfi3ivol7s2r",
    # "at://did:plc:hx53snho72xoj7zqt5uice4u/app.bsky.graph.list/3l7smvoqdi62r"
]

# kasey_handles = get_list_items("at://did:plc:hx53snho72xoj7zqt5uice4u/app.bsky.graph.list/3kivqnnhzcr27")
handles = []  

for uri in uris:
    items = get_list_items(uri)
    for item in items:
        subject = item.get("subject")
        if subject:
            handle = subject.get("handle")
            if handle:
                handles.append(handle)

with open("handles2.txt", "w") as file:
    for handle in handles:
        file.write(handle + "\n")

print("Handles written to handles2.txt")

# save_json(kasey_handles)

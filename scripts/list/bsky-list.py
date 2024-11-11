
#!/usr/bin/env python

import requests
import json
from datetime import datetime, timedelta, timezone
import sys
import mimetypes
import time

credentials = {
    'username': "",
    'password': ""
}

def get_session():
    url = 'https://bsky.social/xrpc/com.atproto.server.createSession'

    payload = {
        'identifier': credentials["username"],
        'password': credentials["password"]
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get access token. Status code: {response.status_code}. Response: {response.text}")
        
def get_service_endpoint(did):
    url = f"https://plc.directory/{did}"
    response = requests.get(url)
    if response.status_code == 200:
        services = response.json().get('service')
        for service in services:
            if service['type'] == 'AtprotoPersonalDataServer':
                return service['serviceEndpoint']
        raise Exception("PDS serviceEndpoint not found in DID document.")
    else:
        raise Exception(f"Failed to get DID document. Status code: {response.status_code}. Response: {response.text}")

def url2uri(post_url):
    parts = post_url.rstrip('/').split('/')
    if len(parts) < 4: raise ValueError(f"Post URL '{post_url}' does not have enough segments.")
    rkey, username = parts[-1], parts[-3]
    return f"at://{resolve_did(username)}/app.bsky.feed.post/{rkey}"

def resolve_did(handle):
    if handle.startswith("did:"): return handle 
    response = requests.get(f'https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle={handle}')
    if response.status_code != 200: raise Exception(f"Failed to resolve DID: '{response.text}'")
    return response.json()['did']

def decompose_uri(uri):
    uri_parts = uri.replace("at://", "").split("/")
    repo = uri_parts[0]
    collection = uri_parts[1]
    rkey = uri_parts[2]
    return repo, collection, rkey

def uri2url(uri):
    print("TODO")

def view_list():
    #getList
    print("wip")

def get_lists(actor):
    #getLists

    params = {
        'actor': actor,
        'limit': 10
    }

    response = requests.get('https://public.api.bsky.app/xrpc/app.bsky.graph.getLists', headers={'Content-Type': 'application/json'}, params=params)

    if response.status_code == 200:
        return response.json()["lists"]
    else:
        raise Exception(f"Failed to create post. Status code: {response.status_code}. Response: {response.text}")

def display_lists(lists):
    # print(json.dumps(lists, indent=3))
    # filename = f"{credentials['username']}-lists"
    # json.dump(lists, open(f'{filename}.json', 'w'), indent=4), print(f"JSON extracted to '{filename}.json'")

    # names = {}
    print()
    for i in range(len(lists)):
        name = lists[i]["name"]
        item_count = lists[i]["listItemCount"]
        print(f"\t{i+1}: \t{name}\t{item_count}")
        # names[name] = lists[i]["description"]
        # names[name] = {
        #     "description": description,
        #     "item_count": item_count
        # }
    print()
    # return names
    # for idx, item in enumerate(lists):
    #     name = item["name"]
    #     item_count = item.get("listItemCount", 0)
    #     print(f"{idx + 1}: \t{name}\t{item_count}")

def select_list(lists):
    sel = int(input("Select a list: "))
    sel = sel - 1
    selected_list = lists[sel]
    print(f"List Selected: {selected_list["name"]}")
    print(f"Description: {selected_list["description"]}")
    return selected_list

def create_list(session, service_endpoint):
    #createRecord
    did = session['did']
    url = f"{service_endpoint}/xrpc/com.atproto.repo.createRecord"

    name = input("Enter new list name: ")
    description = input("Enter new list description: ")

    payload = json.dumps({
    "repo": did,
    "collection": "app.bsky.graph.list",
    "record": {
        "$type": 'app.bsky.graph.list',
        "purpose": 'app.bsky.graph.defs#curatelist',
        "name": name,
        "description": description,
        "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    })

    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {session.get('accessJwt')}'
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        rkey = response.json().get('uri').rstrip('/').split('/')[-1]
        print(f"List successfully created: https://bsky.app/profile/{session.get('handle')}/lists/{rkey}")
    else:
        raise Exception(f"Failed to create post. Status code: {response.status_code}. Response: {response.text}")

def get_list_record(session, service_endpoint, selected_list):
    # did = session['did']
    # rkey = selected_list['uri'].rstrip('/').split('/')[-1]
    did, collection, rkey = decompose_uri(selected_list['uri'])
    
    url = f"{service_endpoint}/xrpc/com.atproto.repo.getRecord"

    params = {
        "repo": did,
        "collection": collection, # "app.bsky.graph.list",
        "rkey": rkey,
    }

    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {session.get('accessJwt')}'
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data["value"], data["uri"]
    else:
        raise Exception(f"Failed to create post. Status code: {response.status_code}. Response: {response.text}")

def update_list_metadata(session, service_endpoint, selected_list, name=None, description=None):
    #putRecord

    record, uri = get_list_record(session, service_endpoint, selected_list)
    # print(json.dumps(record, indent=3))
    # filename = f"{credentials['username']}-{record["name"]}"
    # json.dump(record, open(f'{filename}.json', 'w'), indent=4), print(f"JSON extracted to '{filename}.json'")
    # exit()

    if name == None:
        record["name"] = input("New name for list: ")
    else:
        record["name"] = name
    if description == None:
        record["description"] = input("New description for list: ")
    else:
        record["description"] = description

    did, collection, rkey = decompose_uri(uri)
    url = f"{service_endpoint}/xrpc/com.atproto.repo.putRecord"

    payload = json.dumps({
        "repo": did,
        "collection": collection, # "app.bsky.graph.list",
        "rkey": rkey,
        "record": record,
    })

    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {session.get('accessJwt')}'
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        rkey = response.json().get('uri').rstrip('/').split('/')[-1]
        print(f"List successfully updated: https://bsky.app/profile/{session.get('handle')}/lists/{rkey}")
    else:
        raise Exception(f"Failed to create post. Status code: {response.status_code}. Response: {response.text}")

def delete_list(session, service_endpoint, selected_list):
    #deleteRecord
    record, uri = get_list_record(session, service_endpoint, selected_list)
    did, collection, rkey = decompose_uri(uri)
    url = f"{service_endpoint}/xrpc/com.atproto.repo.deleteRecord"

    payload = json.dumps({
        "repo": did,
        "collection": collection,
        "rkey": rkey,
    })

    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {session.get('accessJwt')}'
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        print(f"List successfully deleted")
    else:
        raise Exception(f"Failed to create post. Status code: {response.status_code}. Response: {response.text}")

def add_user_to_list(session, service_endpoint, selected_list, user_did):
    #createRecord
    list_uri = selected_list['uri']
    did, collection, rkey = decompose_uri(list_uri)
    url = f"{service_endpoint}/xrpc/com.atproto.repo.createRecord"

    payload = json.dumps({
    "repo": did,
    "collection": 'app.bsky.graph.listitem',
    "record": {
        "$type": 'app.bsky.graph.listitem',
        "subject": user_did,
        "list": list_uri,
        "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    })

    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {session.get('accessJwt')}'
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        print(f"{user_did} successfully added to list '{selected_list["name"]}'")
        # print(f"https://bsky.app/profile/{session.get('handle')}/lists/{rkey}")
    else:
        raise Exception(f"Failed to create post. Status code: {response.status_code}. Response: {response.text}")

def remove_user_from_list():
    #deleteRecord
    # retrieve all listitem records for a given list
    # search for a given user [handle, did, whatever]
    # grab uri of that record and decompose_uri
    # then deleteRecord({repo, collection, rkey})
    print("wip")

def get_follows(did):
    service_endpoint = get_service_endpoint(did)
    url = f"{service_endpoint}/xrpc/com.atproto.repo.listRecords"
    PAGE_LIMIT = 100

    def fetch_page(cursor=None):
        params = {
            "repo": did,
            "collection": "app.bsky.graph.follow",
            "limit": PAGE_LIMIT,
            "cursor": cursor,
        }
        response = requests.get(url, headers={'Content-Type': 'application/json'}, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get follow records. Status code: {response.status_code}. Response: {response.text}")

    # Initial fetch
    res = fetch_page()
    follows = res["records"]

    # Continue fetching pages while there's a cursor and a full page of records
    while res.get("cursor") and (len(res["records"]) >= PAGE_LIMIT):
        res = fetch_page(res["cursor"])
        follows.extend(res["records"])

    # print_dict = {}
    # print_dict['mrow'] = follows
    # filename = f"{credentials['username']}-follows"
    # json.dump(print_dict, open(f'{filename}.json', 'w'), indent=4), print(f"JSON extracted to '{filename}.json'")

    return follows

def bad_get_follows(session):
    #bloat and unfinished
    PAGE_LIMIT = 100
    did = session["did"]
    url = "https://public.api.bsky.app/xrpc/app.bsky.graph.getFollows"
    
    def fetch_page(cursor=None):
        params = {
            "actor": did,
            "limit": PAGE_LIMIT,
            "cursor": cursor,
        }
        return requests.get(url, headers={'Content-Type': 'application/json'}, params=params)

    # Initial fetch
    res = fetch_page()
    follows = res["data"]["follows"]

    # Continue fetching pages while there's a cursor and a full page of records
    while res["data"].get("cursor") and (len(res["data"]["follows"]) >= PAGE_LIMIT):
        res = fetch_page(res["data"]["cursor"])
        follows.extend(res["data"]["records"])
    
    return follows

def add_follows_to_list():
    session = get_session()
    did = session['did']
    service_endpoint = get_service_endpoint(did)
    lists = get_lists(did)
    display_lists(lists)
    selected_list = select_list(lists)

    follows = get_follows(did)
    for i in range(len(follows)):
        add_user_to_list(session, service_endpoint, selected_list, follows[i]['value']['subject'])

    update_list_metadata(session, service_endpoint, selected_list, name=selected_list['name'], description=f"Last updated {datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}")

    print()
    _, _, rkey = decompose_uri(selected_list['uri'])
    print(f"All followers successfully added to https://bsky.app/profile/{selected_list['creator']['handle']}/lists/{rkey}")

def main():
    session = get_session()
    print(session['handle'])
    # did = session['did']
    # service_endpoint = get_service_endpoint(did)

    # create_list(session, service_endpoint)
    # time.sleep(5)

    lists = get_lists(credentials['username'])
    # lists = get_lists(did)
    display_lists(lists)
    selected_list = select_list(lists)

    # update_list_metadata(session, service_endpoint, selected_list)
    # delete_list(session, service_endpoint, selected_list)

    # follows = get_follows(did)

if __name__ == "__main__":
    main()
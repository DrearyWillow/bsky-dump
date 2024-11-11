
# response = requests.get('https://public.api.bsky.app/xrpc/app.bsky.feed.getPostThread', headers={'Content-Type': 'application/json'}, params=params)
# # response = requests.get('https://public.api.bsky.app/xrpc/app.bsky.feed.getQuotes', headers={'Content-Type': 'application/json'}, params={'uri': at_uri, 'limit': 100})
# if response.status_code != 200: raise Exception(f"Failed to retrieve post thread: '{response.text}'")

import requests

# def get_service_endpoint(did):
#     if did.startswith("did:plc"):
#         url = f"https://plc.directory/{did}"
#     else:
#         url = f"https://{did}/.well-known/did.json"

#     response = requests.get(url)
#     if response.status_code == 200:
#         services = response.json().get('service')
#         for service in services:
#             if service['type'] == 'AtprotoPersonalDataServer':
#                 return service['serviceEndpoint']
#         raise Exception("PDS serviceEndpoint not found in DID document.")
#     else:
#         raise Exception(f"Failed to get DID document. Status code: {response.status_code}. Response: {response.text}")

def get_service_endpoint(did):
    if did.startswith("did:plc"):
        url = f"https://plc.directory/{did}"
        response = requests.get(url)
        services = response.json()['service']
    elif did.startswith("did:web"):
        url = f"https://{did}/.well-known/did.json"
        response = requests.get(url)
        services = response.json()['service']
    else:
        url = f"https://resolver.identity.foundation/1.0/identifiers/{did}"
        response = requests.get(url)
        services = response.json()['didDocument']['service']

    for service in services:
        if service['type'] == 'AtprotoPersonalDataServer':
            return service['serviceEndpoint']
    raise Exception("PDS serviceEndpoint not found in DID document.")

    # # response = requests.get(url)
    # if response.status_code == 200:
    #     services = response.json().get('service')
    #     for service in services:
    #         if service['type'] == 'AtprotoPersonalDataServer':
    #             return service['serviceEndpoint']
    #     raise Exception("PDS serviceEndpoint not found in DID document.")
    # else:
    #     raise Exception(f"Failed to get DID document. Status code: {response.status_code}. Response: {response.text}")


path = '/home/kyler/Downloads/bsky-swag.mp4'
# did = "did:plc:7x6rtuenkuvxq3zsvffp2ide" # bunny
# did = "did:web:genco.me" # genco
did = "did:plc:hx53snho72xoj7zqt5uice4u" # me 
cid = "bafkreihe23afqwtv2goq7lpgdojdvrlfflrs2ukrftdvllq2vo5zopb4om" # my video
# cid = "bafkreielhgekjheckgjusx7x5hxkbrqryfdmzdwwp2zoxchovgnpzkxzae" # bunny video
# # cid = "bafkreihwyaug7exifmkuoub5zbgxhowvvvljgz5ciphubotg5ae66o4vby" # bunny image
service_endpoint = get_service_endpoint(did)
print(service_endpoint)
# # exit()
response = requests.get(f'{service_endpoint}/xrpc/com.atproto.sync.getBlob?did={did}&cid={cid}')
# # response = requests.get(f"https://pds.bun.how/xrpc/com.atproto.sync.getBlob?did=did:plc:7x6rtuenkuvxq3zsvffp2ide&cid=bafkreielhgekjheckgjusx7x5hxkbrqryfdmzdwwp2zoxchovgnpzkxzae")
if response.status_code != 200: raise Exception(f"Failed to retrieve post thread: '{response.text}'")
with open(path, 'wb') as f: f.write(response.content)
print(f"Blob successfully downloaded to {path}")


# response = requests.get(f"https://resolver.identity.foundation/1.0/identifiers/{did}")
# if response.status_code != 200: raise Exception(f"Failed to retrieve post thread: '{response.text}'")
# # print(response.content)
# # print(response.json()['didDocument']['service']['serviceEndpoint'])

# services = response.json()['didDocument']['service']
# for service in services:
#     if service['type'] == 'AtprotoPersonalDataServer':
#         print(service['serviceEndpoint'])
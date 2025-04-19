from bsky_utils import *

# handle = 'dreary.dev'
# did = resolve_handle(handle)
# service = get_service_endpoint(did)
# path = f'{generate_timestamp()}-{handle}.car'
did = 'did:plc:hx53snho72xoj7zqt5uice4u'
service = 'https://porcini.us-east.host.bsky.network/'
path = f'/mnt/Archive/.inactive/Me/repo/{generate_timestamp()}.car'

get_repo(did, service, path)

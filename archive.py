
from bsky_utils import *

handle = ""
did = resolve_handle(handle)
pw = ""
service = get_service_endpoint(did)
session = get_session(handle, pw, service)

blob_path = '/home/kyler/Downloads/outie.juli.ee.zip'
blob = upload_blob(session, service, blob_path)

record = {
    '$type': 'dev.dreary.archive',
    'createdAt': generate_timestamp(),
    'blob': blob
}

create_record(session, service, record)
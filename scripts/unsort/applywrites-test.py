from bsky_utils import *

did = resolve_handle("dreary.dev")
service = get_service_endpoint(did)
session = get_session(did, "@11LoveLain!", service)

records = []

for i in range(5):
    records.append({
        "$type": "dev.dreary.test",
        "count": i
    })

# apply_writes_create(session, service, 'dev.dreary.test', records, view_json=True)

apply_writes_create(session, service, records, view_json=True)

from bsky_api import *
import sys

with open("yield.json", "r") as file:
    ydata = json.load(file)

with open("return.json", "r") as file:
    rdata = json.load(file)

dupe, mcount, unmatch, total = 0, 0, 0, 0
matching = {}
matching['dupe'] = []
matching['match'] = []
matching['unmatch'] = []
for did in ydata:
    handle = ydata[did]
    if did in rdata:
        if did in matching:
            matching["dupe"].append({'did': did, 'handle': handle})
            dupe += 1
        else:
            matching["match"].append({'did': did, 'handle': handle})
            mcount += 1
    else:
        matching["unmatch"].append({'did': did, 'handle': handle})
        unmatch += 1
    total += 1
print(f"Match  : {mcount}")
print(f"Dupe   : {dupe}")
print(f"Unmatch: {unmatch}")
print(f"Total  : {total}")
print(f"Yield  : {len(ydata)}")
print(f"Return : {len(rdata)}")

save_json(matching)
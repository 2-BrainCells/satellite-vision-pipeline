import json
from processing import perform_change_detection
geo='{"type":"Polygon","coordinates":[[[85.82,20.29],[85.83,20.29],[85.83,20.30],[85.82,20.30],[85.82,20.29]]]}'
print(json.dumps(perform_change_detection(geo), indent=2))

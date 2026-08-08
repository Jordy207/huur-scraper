import requests
import json
a = requests.get("https://admin.nrw-wonen.nl/api/v1/aanbod")

for i in a.json()[0]:
    print(i)

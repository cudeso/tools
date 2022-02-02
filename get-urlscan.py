import requests
import json

key=""

r="be"
q="domain:{}".format(r)

result = requests.get("https://urlscan.io/api/v1/search/?q={}&size=250".format(q))
if "results" in result.json():
    l = open("{}.log".format(r),"w")
    for r in result.json()["results"]:
        screenshot = ""
        _id = r["_id"]
        print("{},{},{},{}".format(r["indexedAt"],r["task"]["url"], r["result"], r["screenshot"]))
        l.write("{},{},{},{}".format(r["indexedAt"],r["task"]["url"], r["result"], r["screenshot"]))
        screenshot = r["screenshot"]
        if screenshot:
            s = requests.get(screenshot)
            open("{}.png".format(_id), 'wb').write(s.content)

#print(result.text.encode())




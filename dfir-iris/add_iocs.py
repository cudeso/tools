import requests
import csv
import json
from requests_toolbelt.utils import dump

iris_host="https://case:4433/"
iris_apikey="IRIS_APIKEY"
iris_headers={"Authorization": "Bearer {}".format(iris_apikey), "Content-Type": "application/json"}
iris_verify=False

misp_host="https://misp/"
misp_apikey="MISP_APIKEY"
misp_headers={"Authorization": misp_apikey, "Accept": "application/json", "Content-Type": "application/json"}
misp_verify=False
misp_data=json.dumps({"returnFormat": "json", "tags": ["customer:CORP"],"to_ids":"1"})

case_id = 1
tlp_code = 2

indicators=requests.post("{}/attributes/restSearch".format(misp_host), headers=misp_headers, data=misp_data, verify=misp_verify)
response=indicators.json()["response"]["Attribute"]
for attr in response:
    ioc_tags = ""
    value=attr["value"]
    if 'Tag' in attr:
        for t in attr["Tag"]:
            ioc_tags += t["name"] + ","

    attr_type=attr["type"]
    if attr_type in ["ip-src","ip-dst"]:
        attr_type="IP"
    elif attr_type in ["md5", "sha1", "sha256"]:
        attr_type="Hash"
    elif attr_type in ["hostname", "domain"]:
        attr_type="Domain"

    iris_data=json.dumps({"ioc_type": attr_type, "ioc_tlp_id": tlp_code, "ioc_value": value, "ioc_description": "From MISP", "ioc_tags": ioc_tags, "cid": case_id})
    result = requests.post("{}/case/ioc/add".format(iris_host), headers=iris_headers, data=iris_data, verify=iris_verify)
    print(dump.dump_all(result))
import json
import requests
import datetime

MATTERMOST_VERIFY_CERT = False
MATTERMOST_WEBHOOK = False
STATBEL_ID = "ef2a5bfb-a361-47a6-b113-e3df26563404"
STATBEL_URL = "https://bestat.statbel.fgov.be/bestat/api/views/{}/result/JSON"

def send_notification(data: dict):
    payload = {"text": json.dumps(data, indent=2)}
    try:
        response = requests.post(
            MATTERMOST_WEBHOOK,
            json=payload,
            timeout=10,
            verify=MATTERMOST_VERIFY_CERT
        )
        response.raise_for_status()
    except Exception as err:
        print(err)

def get_today():
    return datetime.datetime.now().strftime("%d%b%y").lower()

def main():
    today = get_today()

    url = STATBEL_URL.format(STATBEL_ID)
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    facts = data["facts"]

    wanted_products = [
        #"propaan (in bulk) (vanaf 2000 l) (€/l)",
        "propaan (in bulk) (minder dan 2000 l) (€/l)"
    ]
    wanted_products_lower = [p.lower() for p in wanted_products]

    results = {}
    for fact in facts:
        dag = fact.get("Dag", "").lower()
        productgroep = fact.get("Productgroep", "").lower()
        product = fact.get("Product", "").lower()
        value = fact.get("Prijs incl. BTW")

        # Normalize product for matching
        product_norm = product.replace("€/l", "€/l").replace("€/L", "€/l")

        # Match today's date and wanted products
        if dag == today and productgroep == "propaan":
            for wanted in wanted_products_lower:
                if product_norm == wanted:
                    results[wanted] = value

    for name in wanted_products:
        send_notification(f"{name}: **{results.get(name.lower(), 'N/A')}**")

if __name__ == "__main__":
    main()
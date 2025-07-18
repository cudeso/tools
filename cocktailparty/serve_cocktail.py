import asyncio
import requests
import json
import websockets
import logging
import re
from datetime import datetime

COCKTAIL_HIGHLIGHT = [".be$", "bank"]

MATTERMOST_WEBHOOK=""
WS_APIKEY = ""

COCKTAIL_CERTIFICATES = ["0", "0", "feed:5", "phx_join", {}]
COCKTAIL_CERTIFICATES_FEED="feed:5"
COCKTAIL_NEW_DOMAINS = ["0", "0", "feed:4", "phx_join", {}]
COCKTAIL_NEW_DOMAINS_FEED="feed:4"
WS_JOIN = COCKTAIL_NEW_DOMAINS
WS_JOIN = COCKTAIL_CERTIFICATES


COCKTAIL_LOG="cocktailparty.log"
WS_URL = f"wss://cocktailparty.lu/feedsocket/websocket?token={WS_APIKEY}&vsn=2.0.0"
ALLOWED_UPDATE_TYPES = {"X509LogEntry"}
MATTERMOST_VERIFY_CERT=False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(COCKTAIL_LOG),
    ]
)
logger = logging.getLogger(__name__)

def matches_highlight(cn_or_san: str, _unused=None) -> bool:
    for h in COCKTAIL_HIGHLIGHT:
        if h.endswith('$'):
            pattern = re.compile(h)
            if pattern.search(cn_or_san or ""):
                logger.info(f"Match {cn_or_san}")
                return True
        else:
            if h == (cn_or_san or ""):
                return True
    return False

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
        logger.info(f"Successfully posted to Mattermost")
    except Exception as err:
        logger.error(f"Failed to post to Mattermost {err}")

async def consume():
    logger.info("Start")
    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps(WS_JOIN))
        feed_type = WS_JOIN[2]

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)

                if not (isinstance(data, list) and len(data) >= 5 and isinstance(data[4], dict)):
                    continue

                if feed_type == COCKTAIL_CERTIFICATES_FEED:
                    payload = data[4].get("payload", {})
                    cert_data = payload.get("data", {})
                    leaf_cert = cert_data.get("leaf_cert", {})

                    update_type = cert_data.get("update_type", "")
                    if update_type not in ALLOWED_UPDATE_TYPES:
                        continue

                    subject = leaf_cert.get("subject", {})
                    extensions = leaf_cert.get("extensions", {})

                    cn = subject.get("CN", "")
                    san = extensions.get("subjectAltName", "")
                    seen = cert_data.get("seen", None)
                    domains = leaf_cert.get("all_domains", [])
                    source = cert_data.get("source", {}).get("name", "")
                    fingerprint = leaf_cert.get("fingerprint", "")
                    cert_link = cert_data.get("cert_link", "")

                    if matches_highlight(cn, san):
                        result = {
                            "CN": cn,
                            "SAN": san,
                            "Domains": domains,
                            "Source Log": source,
                            "Fingerprint": fingerprint,
                            "Cert Link": cert_link,
                            "Timestamp": datetime.utcfromtimestamp(seen).isoformat() if seen else None,
                            "Type": update_type
                        }
                        send_notification(result)

                elif feed_type == COCKTAIL_NEW_DOMAINS_FEED:
                    raw_payload = data[4].get("payload", "")
                    try:
                        parsed_payload = json.loads(raw_payload)
                        domain_list = parsed_payload.get("data", [])
                        for domain in domain_list:
                            if matches_highlight(domain):
                                result = {
                                    "New Domain": domain,
                                    "Timestamp": datetime.utcnow().isoformat()
                                }
                                send_notification(result)
                    except json.JSONDecodeError:
                        continue

            except (json.JSONDecodeError, KeyError, TypeError):
                continue
            except KeyboardInterrupt:
                logger.error("Interrupted by user.")
                break

asyncio.run(consume())
logger.info("End")
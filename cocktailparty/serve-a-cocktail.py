import asyncio
import requests
import json
import websockets
import logging
import re
from datetime import datetime
from config import *

COCKTAIL_CERTIFICATES = ["0", "0", "feed:5", "phx_join", {}]
COCKTAIL_CERTIFICATES_FEED = "feed:5"
COCKTAIL_NEW_DOMAINS = ["0", "0", "feed:4", "phx_join", {}]
COCKTAIL_NEW_DOMAINS_FEED = "feed:4"

COCKTAIL_LOG = "cocktailparty.log"
WS_URL = f"wss://cocktailparty.lu/feedsocket/websocket?token={WS_APIKEY}&vsn=2.0.0"
ALLOWED_UPDATE_TYPES = {"X509LogEntry"}
MATTERMOST_VERIFY_CERT = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(COCKTAIL_LOG),
    ]
)
logger = logging.getLogger(__name__)


def matches_highlight(entry: list[str]) -> bool:
    for domain in entry:
        for h in COCKTAIL_HIGHLIGHT:
            if h.endswith('$'):
                pattern = re.compile(h)
                if pattern.search(domain or ""):
                    logger.info(f"Match {domain}")
                    return True
            else:
                if h in domain:
                    logger.info(f"Match {domain}")
                    return True
    return False


def send_notification(data: dict, feed_type):
    message = False
    if feed_type == COCKTAIL_CERTIFICATES_FEED:
        message = f"New certificate update for **{data.get('Domains', 'Unknown domains')}**\n\n"
        message += f"- CN: **{data.get('CN', 'Unknown CN')}**\n"
        message += f"- SAN: **{data.get('SAN', 'Unknown SubjectAltName')}**\n"
        message += f"- Source Log: {data.get('Source Log', 'Unknown source')}\n"
        message += f"- Fingerprint: {data.get('Fingerprint', 'Unknown Fingerprint')}\n"
        message += f"- Cert Link: {data.get('Cert Link', 'Unknown Cert Link')}\n"
        message += f"- Timestamp: {data.get('Timestamp', 'Unknown Timestamp')}\n"
    elif feed_type == COCKTAIL_NEW_DOMAINS_FEED:
        message = f"New domain registered: **{data.get('Domain', 'Unknown domain')}**\n"
        message += f"- Timestamp: {data.get('Timestamp', 'Unknown Timestamp')}\n"
                         
    if message:
        payload = {"text": message}
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


async def consume(shutdown_event: asyncio.Event):
    logger.info("Start")
    try:
        async with websockets.connect(WS_URL) as ws:
            # Subscribe to both feeds
            await ws.send(json.dumps(COCKTAIL_CERTIFICATES))
            await ws.send(json.dumps(COCKTAIL_NEW_DOMAINS))

            while not shutdown_event.is_set():
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=1)
                    data = json.loads(msg)

                    # Check for correct structure
                    if not (isinstance(data, list) and len(data) >= 5 and isinstance(data[2], str) and isinstance(data[4], dict)):
                        continue

                    feed_type = data[2]

                    if feed_type == COCKTAIL_CERTIFICATES_FEED:
                        payload = data[4].get("payload", {})
                        try:
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

                            if matches_highlight(domains):
                                send_notification({
                                    "CN": cn,
                                    "SAN": san,
                                    "Domains": domains,
                                    "Source Log": source,
                                    "Fingerprint": fingerprint,
                                    "Cert Link": cert_link,
                                    "Timestamp": datetime.utcfromtimestamp(int(seen)).isoformat() if seen else None,
                                    "Type": update_type
                                }, feed_type)
                        except json.JSONDecodeError:
                            continue

                    elif feed_type == COCKTAIL_NEW_DOMAINS_FEED:
                        raw_payload = data[4].get("payload", "")
                        try:
                            parsed_payload = json.loads(raw_payload)
                            domains = parsed_payload.get("data", [])
                            for domain in domains:
                                if matches_highlight([domain]):
                                    send_notification({
                                        "Domain": domain,
                                        "Timestamp": datetime.utcnow().isoformat(),
                                    }, feed_type)

                        except json.JSONDecodeError:
                            continue

                except asyncio.TimeoutError:
                    continue  # Allows checking shutdown_event periodically
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue
    except Exception as e:
        logger.error(f"Websocket error: {e}")
    finally:
        logger.info("Websocket closed")


shutdown_event = asyncio.Event()
try:
    asyncio.run(consume(shutdown_event))
except KeyboardInterrupt:
    logger.error("Interrupted by user.")
    shutdown_event.set()

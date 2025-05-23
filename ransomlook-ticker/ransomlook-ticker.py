#!/usr/bin/env python3

import json
import sys
from typing import Any, Dict, List, Union
import requests
from requests.exceptions import HTTPError, RequestException, Timeout
import openai
import logging
#import os
from typing import List, Dict
from config import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(RANSOMLOOK_LOG),
        #logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_last_posts() -> List[Dict[str, Any]]:
    resp = requests.get(
        RANSOMLOOK_API_URL,
        headers={"accept": "application/json"},
        timeout=10,
        verify=True
    )
    resp.raise_for_status()
    return resp.json()


def google_search(query: str, k: int = 10) -> List[Dict[str, str]]:
    url = "https://customsearch.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": min(k, 10),
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    docs = []
    for item in data.get("items", []):
        docs.append(
            f"Title: {item.get('title', '')}\n"
            f"Snippet: {item.get('snippet', '')}\n"
            f"Link: {item.get('link', '')}"
        )

    logger.info(f"Google search results for query '{query}': {len(docs)} results")
    logger.debug(f"Google search results: {docs}")
    return "\n\n".join(docs)


def enrich_post(title: str, description: str) -> Dict[str, Any]:
    snippets = google_search(title, k=5)
    prompt = PROMPT_TEMPLATE.format(title=title, description=description, snippets=snippets)
    openai.api_key = OPENAPI_KEY
    response = openai.chat.completions.create(
        model=OPENAPI_MODEL,
        temperature=OPENAPI_TEMPERATURE,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a threat intelligence assistant supporting a CTI team tracking ransomware incidents."},
            {"role": "user", "content": prompt},
        ],
    )
    return json.loads(response.choices[0].message.content)


def save_results(enriched: List[Dict[str, Any]]) -> None:
    try:
        with open(RANSOMLOOK_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(enriched, f, indent=4, ensure_ascii=False)
    except Exception as err:
        logger.error(f"Failed to write results to {RANSOMLOOK_OUTPUT}: {err}")
        return


def print_results(enriched: List[Dict[str, Any]]) -> None:
    for post in enriched:
        print(f"Company: {post['company_name']}")
        print(f"Ransomware Group: {post['group_name']}")
        print(f"Discovered: {post['discovered']}")
        print(f"Country: {post['country']}")
        print(f"Sector: {post['sector']}")
        print(f"URL: {post['url']}")
        print(f"Description: {post['description']}")
        print(f"Summary: {post['summary']}")
        print("-" * 40)


def load_existing_data() -> List[Dict[str, Any]]:
    try:
        with open(RANSOMLOOK_OUTPUT, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as err:
        logger.error(f"Failed to load existing data from {RANSOMLOOK_OUTPUT}: {err}")
        return []


def notify_results(enriched: List[Dict[str, Any]]) -> None:
    for post in enriched:
        country = post['country']
        sector = post['sector']
        company = post['company_name']

        highlight = country in HIGHLIGHT_TICKER or (
            isinstance(sector, list) and any(s in HIGHLIGHT_TICKER for s in sector)
        ) or (isinstance(sector, str) and sector in HIGHLIGHT_TICKER)

        message = (
            "New ransomware post detected!\n\n"
            f"- Company: **{company}**\n"
            f"- Ransomware Group: **{post['group_name']}**\n"
            f"- Discovered: **{post['discovered']}**\n"
            f"- Country: **{country}**\n"
            f"- Sector: **{', '.join(sector) if isinstance(sector, list) else sector}**\n"
            f"- URL: **{post['url']}**\n"
            f"- Description: **{post['description']}**\n"
            f"- Summary: **{post['summary']}**\n"
        )

        if highlight:
            message = (
                f"**:rotating_light: HIGHLIGHTED POST :rotating_light:**\n\n{message}"
            )

        payload = {"text": message}

        try:
            response = requests.post(
                MATTERMOST_WEBHOOK,
                json=payload,
                timeout=10,
                verify=MATTERMOST_VERIFY_CERT
            )
            response.raise_for_status()
            logger.info(f"Successfully posted to Mattermost: {company}")
        except Exception as err:
            logger.error(f"Failed to post to Mattermost for {company}: {err}")


def main() -> None:
    logger.info("Starting RansomLook ticker")

    existing_data = load_existing_data()
    existing_entries = {
        (entry["post_title"], entry["group_name"], entry["discovered"])
        for entry in existing_data
    }

    logger.info("Fetching latest posts from RSS feed.")
    try:
        raw_posts = get_last_posts()
    except Exception as err:
        logger.error(f"[fetch] {err}")
        sys.exit(1)

    enriched: List[Dict[str, Any]] = []

    for post in raw_posts:
        title = post.get("post_title", "").strip()
        group_name = post.get("group_name", "").strip()
        discovered = post.get("discovered", "").strip()
        description = post.get("description", "").strip()

        if (title, group_name, discovered) in existing_entries:
            logger.info(f"Skipping already processed post: {title}")
            continue

        logger.info(f"Starting LLM query for post: {title}")
        try:
            extra = enrich_post(title, description)
        except Exception as err:
            logger.error(f"Error before LLM query  {title!r}: {err}")
            continue

        enriched.append({
            "post_title": title,
            "discovered": discovered,
            "description": description,
            "group_name": group_name,
            **extra
        })

    all_data = existing_data + enriched

    save_results(all_data)
    notify_results(enriched)

    logger.info("Finished processing posts")


if __name__ == "__main__":
    main()

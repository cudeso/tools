
# In channel; do "/invite @app"

'''
Download files from a Slack channel. 
Focus on one specific user

'''

import os
from slack_sdk import WebClient
import requests
import re

def get_filename(url):
    url_split = url.split("/")
    return url_split[len(url_split) - 1]


slack_token = "TOKEN"
channel_id = "CHANNEL_ID"
user_id = "USER_ID"
client = WebClient(token=slack_token)

conversation_history = []

result = client.conversations_history(channel=channel_id)

conversation_history = result["messages"]

for message in conversation_history:
    if message["user"] == user_id:
        if "files" in message:
            for file in message["files"]:
                url_private = file["url_private"]
                headers = { 'Authorization': 'Bearer {}'.format(slack_token) }
                r = requests.get(url_private, allow_redirects=True, headers=headers)
                filename = get_filename(url_private)
                open(filename, 'wb').write(r.content)

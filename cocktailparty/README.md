# CocktailParty

CocktailParty is the CIRCL **CTI data streaming** platform: [https://cocktailparty.lu/](https://cocktailparty.lu/).

It supports three data streams:

- Certificate Transparency: **newly registered certificates**
- Certificate Transparency: **newly registered domains**
- Certificate Transparency: **newly registered certificates (full)**

You can subscribe to the stream with [websocat](https://github.com/vi/websocat/releases), but I created a small Python script to make filtering data easier.

# Serve a Cocktail

The `serve-a-cocktail.py` script is a Python client for CocktailParty. Its main features:

- **WebSocket subscription**: Connects to the WebSocket API to receive real-time data streams about newly registered certificates and domains.
- **Custom filtering**: Filters incoming certificate and domain events based on user-defined highlight patterns.
- **Notification integration**: Sends filtered results as notifications to a Mattermost channel.
- **Logging**: Writes events and notifications to a local log file.
- **Extensible feeds**: Easily switch between CocktailParty feeds.

## Configuration

Before running the script, set the following configuration options in `config.py`:

- `COCKTAIL_HIGHLIGHT`: A list of keywords or regex patterns to highlight/filter events (e.g., `[".be$", "bank"]`).
- `MATTERMOST_WEBHOOK`: The URL of your Mattermost webhook for notifications.
- `WS_APIKEY`: Your API key for authenticating with CocktailParty.

## Install

Set up a Python virtual environment and install the required libraries:

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

Run the script from the Python virtual environment:

```sh
python serve-a-cocktail.py
```

Optionally, you can run it as a service using systemd. Example systemd unit file (`/etc/systemd/system/serve-a-cocktail.service`):

```
[Unit]
Description=Serve a cocktail
After=network.target

[Service]
Type=simple
WorkingDirectory=/data/cocktailparty/
User=ubuntu
ExecStart=/bin/bash -c '/data/cocktailparty/venv/bin/python serve-a-cocktail.py; wait'
Restart=always

[Install]
WantedBy=multi-user.target
```

## Advice

Your filter, defined in `COCKTAIL_HIGHLIGHT`, greatly affects the usefulness of the notifications. If you receive too many notifications, you may start ignoring them. Recommended approach:

- Add your customer(s) name as a string.
- Add their public domains so you get notified if a new subdomain appears.

## Screenshot

![output.png](output.png)
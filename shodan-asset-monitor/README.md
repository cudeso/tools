# Monitor your assets in Shodan

## Upgrade to v2

If you have an existing sqlite db (from v1) and you want to upgrade the database then do
`sqlite shodan-asset-monitor.db < shodan-asset-monitor_updatedb.sql`

## Change this

* Shodan API key
* Mail sender and receiver
* (optionally) Mail server
* (optionally) PRINT_PROGRESS : no output to screen (for cron-job)

## Usage

First create the sqlite database sqlite3 shodan-asset-monitor.db < shodan-asset-monitor.sql

Give one parameter as the string to search for in Shodan
Second (optional) parameter will disable mail notifications (ideal for first run)

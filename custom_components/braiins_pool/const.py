"""Constants for the Braiins Pool integration."""

DOMAIN = "braiins_pool"
BRAIINS_API_URL = "https://pool.braiins.com/stats/json/btc/"
CONF_API_KEY = "api_key"
DEFAULT_SCAN_INTERVAL = 300  # seconds
API_HEADERS = {"Pool-Auth-Token": "{}"}
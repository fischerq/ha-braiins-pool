"""Constants for the Braiins Pool integration."""

DOMAIN = "braiins_pool"
CONF_API_KEY = "api_key"
CONF_REWARDS_ACCOUNT_NAME = "rewards_account_name"
DEFAULT_SCAN_INTERVAL = 300  # seconds
API_HEADERS = {"Pool-Auth-Token": "{}"}

API_URL_POOL_STATS = "https://pool.braiins.com/stats/json/{}"
API_URL_USER_PROFILE = "https://pool.braiins.com/accounts/profile/json/{}/"
API_URL_DAILY_REWARDS = "https://pool.braiins.com/accounts/rewards/json/{}"
API_URL_DAILY_HASHRATE = "https://pool.braiins.com/accounts/hash_rate_daily/json/{}/{}"
API_URL_BLOCK_REWARDS = (
    "https://pool.braiins.com/accounts/block_rewards/json/{}?from={}&to={}"
)
API_URL_WORKERS = "https://pool.braiins.com/accounts/workers/json/{}/"
API_URL_PAYOUTS = "https://pool.braiins.com/accounts/payouts/json/{}?from={}&to={}"

DEFAULT_COIN = "btc"

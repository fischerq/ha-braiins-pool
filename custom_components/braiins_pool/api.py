"""API client for Braiins Pool."""

import logging
import aiohttp

from .const import BRAIINS_API_URL, API_HEADERS, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)


class BraiinsPoolApiException(Exception):
    """Base exception for Braiins Pool API."""


class BraiinsPoolAuthError(BraiinsPoolApiException):
    """Authentication error."""


class BraiinsPoolApiClient:
    """API client for Braiins Pool."""

    def __init__(self, session: aiohttp.ClientSession, api_key: str):
        """Initialize."""
        self._session = session
        self._api_key = api_key

    async def get_account_stats(self):
        """Fetch account statistics from Braiins Pool API."""
        url = BRAIINS_API_URL  # Assuming this is the stats endpoint
        headers = {
            k: v.format(self._api_key) for k, v in API_HEADERS.items()
        }  # Assuming API_HEADERS uses format strings
        try:
            async with self._session.get(url, headers=headers) as response:
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                return await response.json()
        except aiohttp.ClientResponseError as err:
            if err.status == 401:
                _LOGGER.error("Braiins Pool API Authentication Error: Invalid API key.")
                raise BraiinsPoolAuthError("Invalid API key") from err
            _LOGGER.error(
                "Error fetching account stats from Braiins Pool API: Status %s, %s",
                err.status,
                err.message,
            )
            raise BraiinsPoolApiException(f"API error: Status {err.status}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error(
                "Error fetching account stats from Braiins Pool API: Network or client error: %s",
                err,
            )
            raise err

    async def get_daily_rewards(self):
        """Fetch daily rewards from Braiins Pool API."""
        daily_rewards_url = "https://pool.braiins.com/accounts/rewards/json/btc"
        headers = {k: v.format(self._api_key) for k, v in API_HEADERS.items()}
        try:
            async with self._session.get(
                daily_rewards_url, headers=headers
            ) as response:
                response.raise_for_status()
                data = await response.json()
                # Parse the total_reward from the provided structure
                try:
                    total_reward_str = data["btc"]["daily_rewards"][0]["total_reward"]
                    return float(total_reward_str)
                except (KeyError, IndexError, ValueError) as e:
                    _LOGGER.error("Error parsing daily rewards response: %s", e)
                    # Return None or raise a specific error if parsing fails
                    return None
        except aiohttp.ClientResponseError as err:
            if err.status == 401:
                _LOGGER.error("Braiins Pool API Authentication Error: Invalid API key.")
                raise BraiinsPoolAuthError("Invalid API key") from err
            _LOGGER.error(
                "Error fetching daily rewards from Braiins Pool API: Status %s, %s",
                err.status,
                err.message,
            )
            raise BraiinsPoolApiException(f"API error: Status {err.status}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error(
                "Error fetching daily rewards from Braiins Pool API: Network or client error: %s",
                err,
            )
            raise err

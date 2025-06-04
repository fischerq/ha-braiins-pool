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

    async def _request(self, url: str):
        """Helper method to perform API requests."""
        headers = {
            k: v.format(self._api_key) for k, v in API_HEADERS.items()
        }
        _LOGGER.debug("Making API request to: %s", url)
        try:
            # Assume BRAIINS_API_URL is the base URL and the provided url is the endpoint path
            # If BRAIINS_API_URL is the full URL for stats, the daily rewards URL is also a full URL.
            # This needs to be clarified in const.py or handled differently if not consistent.
            # For now, assuming the provided url is the full endpoint URL.
            async with self._session.get(url, headers=headers) as response:
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                return await response.json()
        except aiohttp.ClientResponseError as err:
            if err.status == 401:
                _LOGGER.error("Braiins Pool API Authentication Error: Invalid API key.")
                raise BraiinsPoolAuthError("Invalid API key") from err
            _LOGGER.error(
                "Error fetching account stats from Braiins Pool API: Status %s, %s",
                response.status,
                await response.text(), # Use response.text() for more detailed error info
            )
            raise BraiinsPoolApiException(
                f"API error {response.status}: {await response.text()}"
            ) from err
        except aiohttp.ClientError as err:
            _LOGGER.error(
                "Error fetching account stats from Braiins Pool API: Network or client error: %s",
                err,
            )
            raise BraiinsPoolApiException(f"Network or client error: {err}") from err

    async def get_account_stats(self):
        """Fetch account statistics from Braiins Pool API."""
        # Assuming BRAIINS_API_URL is the correct endpoint for account stats
        data = await self._request(BRAIINS_API_URL)
        # Return the raw data for the coordinator to process
        return data

    async def get_daily_rewards(self):
        """Fetch daily rewards from Braiins Pool API."""
        # Assuming this is the correct and full URL for daily rewards
        daily_rewards_url = "https://pool.braiins.com/accounts/rewards/json/btc"
        try:
            data = await self._request(daily_rewards_url)
            # Parse the total_reward from the provided structure
            try:
                # Assuming the structure is consistent: data['btc']['daily_rewards'][0]['total_reward']
                # It might be safer to iterate through 'daily_rewards' if there can be multiple entries
                # and sum them up or take the most recent. For now, sticking to the original logic.
                total_reward_str = data.get("btc", {}).get("daily_rewards", [{}])[0].get("total_reward")
                if total_reward_str is None:
                     _LOGGER.warning("Daily rewards data structure unexpected. 'total_reward' not found.")
                     return None
                return float(total_reward_str)
            except (KeyError, IndexError, ValueError) as e:
                _LOGGER.error("Error parsing daily rewards response: %s", e)
                # Return None or raise a specific error if parsing fails
                return None
        except BraiinsPoolApiException:
            # Re-raise the specific API exceptions from the _request helper
            _LOGGER.error(
                "Error fetching daily rewards from Braiins Pool API: Status %s, %s",
                err.status,
                err.message,
            )
            raise BraiinsPoolApiException(f"API error: Status {err.status}") from err
        except aiohttp.ClientError as err:

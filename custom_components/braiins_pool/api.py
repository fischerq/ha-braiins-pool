"""API client for Braiins Pool."""

import logging
import aiohttp

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_HEADERS,
    CONF_API_KEY,
    API_URL_POOL_STATS,
    API_URL_DAILY_REWARDS,
    API_URL_USER_PROFILE,
    API_URL_DAILY_HASHRATE,
    API_URL_BLOCK_REWARDS,
    API_URL_WORKERS,
    API_URL_PAYOUTS,
    DEFAULT_COIN,
)


class BraiinsPoolApiException(Exception):
    """Base exception for Braiins Pool API."""


class BraiinsPoolAuthError(BraiinsPoolApiException):
    """Authentication error."""


class BraiinsPoolApiClient:
    """API client for Braiins Pool."""

    _LOGGER = logging.getLogger(__name__)

    def __init__(self, session: aiohttp.ClientSession, api_key: str):
        """Initialize."""
        self._session = session
        self._api_key = api_key

    async def _request(self, url: str):
        """Helper method to perform API requests."""
        headers = {k: v.format(self._api_key) for k, v in API_HEADERS.items()}
        self._LOGGER.debug("Making API request to: %s", url)
        try:
            # Assume BRAIINS_API_URL is the base URL and the provided url is the endpoint path
            # If BRAIINS_API_URL is the full URL for stats, the daily rewards URL is also a full URL.
            # This needs to be clarified in const.py or handled differently if not consistent.
            # For now, assuming the provided url is the full endpoint URL.
            async with self._session.get(url, headers=headers) as response:
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                return await response.json()
        except aiohttp.ClientResponseError as err:
            if (
                err.status == 403
            ):  # Changed from 401 to 403 based on common API practices for forbidden access with valid key format but insufficient permissions
                self._LOGGER.error(
                    "Braiins Pool API Authentication Error: Invalid API key or insufficient permissions."
                )
                raise BraiinsPoolAuthError("Invalid API key") from err
            self._LOGGER.error(
                "Error fetching account stats from Braiins Pool API: Status %s, %s",
                response.status,
                await response.text(),  # Use response.text() for more detailed error info
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
        url = API_URL_POOL_STATS.format(DEFAULT_COIN)
        return await self._request(url)

    async def get_daily_rewards(self):
        """Fetch daily rewards from Braiins Pool API."""
        url = API_URL_DAILY_REWARDS.format(DEFAULT_COIN)
        return await self._request(url)

    async def get_user_profile(self, coin=DEFAULT_COIN):
        """Fetch user profile from Braiins Pool API."""
        url = API_URL_USER_PROFILE.format(coin)
        return await self._request(url)

    async def get_daily_hashrate(self, group="user", coin=DEFAULT_COIN):
        """Fetch daily hashrate from Braiins Pool API."""
        url = API_URL_DAILY_HASHRATE.format(group, coin)
        return await self._request(url)

    async def get_block_rewards(self, from_date: str, to_date: str, coin=DEFAULT_COIN):
        """Fetch block rewards from Braiins Pool API."""
        url = API_URL_BLOCK_REWARDS.format(coin, from_date, to_date)
        return await self._request(url)

    async def get_workers(self, coin=DEFAULT_COIN):
        """Fetch worker data from Braiins Pool API."""
        url = API_URL_WORKERS.format(coin)
        return await self._request(url)

    async def get_payouts(self, from_date: str, to_date: str, coin=DEFAULT_COIN):
        """Fetch payouts data from Braiins Pool API."""
        url = API_URL_PAYOUTS.format(coin, from_date, to_date)
        return await self._request(url)

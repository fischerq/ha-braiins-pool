"""Data update coordinator for the Braiins Pool integration."""

import asyncio
import logging

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta, datetime

from .const import (
    DOMAIN,
    API_HEADERS,
    CONF_API_KEY,
)

_LOGGER = logging.getLogger(__name__)

from .api import BraiinsPoolApiClient


# Import the actual API client
class BraiinsDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Coordinate updates from the Braiins Pool API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_client: BraiinsPoolApiClient,  # Use the actual API client type hint
        update_interval: timedelta,
    ):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,  # type: ignore [arg-type]
            update_interval=update_interval,
        )
        self.api_client = api_client

    async def _async_update_data(self) -> dict:
        """Fetch data from the API."""
        _LOGGER.debug("Fetching and processing data for Braiins Pool integration.")
        processed_data = {}
        today = datetime.utcnow().date()

        try:
            daily_rewards_data = await self.api_client.get_daily_rewards()
            today_reward_str = (
                daily_rewards_data.get("btc", {})
                .get("daily_rewards", [{}])[0]
                .get("total_reward", "0")
            )
            try:
                processed_data["today_reward"] = float(today_reward_str)
            except (ValueError, KeyError, IndexError):
                _LOGGER.warning(
                    "Could not convert daily reward '%s' to float or access the data. Setting to 0.",
                    today_reward_str,
                )
                processed_data["today_reward"] = 0.0

            user_profile_data = await self.api_client.get_user_profile()
            processed_data["user_profile_data"] = user_profile_data

            daily_hashrate_data = await self.api_client.get_daily_hashrate()
            processed_data["daily_hashrate_data"] = daily_hashrate_data

            # Placeholder dates for now, will refine later
            # Fetch block rewards for the last 7 days
            block_rewards_data = await self.api_client.get_block_rewards(
                (today - timedelta(days=7)).strftime("%Y-%m-%d"),
                today.strftime("%Y-%m-%d"),
            )
            processed_data["block_rewards_data"] = block_rewards_data

            workers_data = await self.api_client.get_workers()
            processed_data["workers_data"] = workers_data

            # Placeholder dates for now, will refine later
            payouts_data = await self.api_client.get_payouts(
                (today - timedelta(days=7)).strftime("%Y-%m-%d"),
                today.strftime("%Y-%m-%d"),
            )
            processed_data["payouts_data"] = payouts_data

            return processed_data
        except Exception as err:  # Catch any exception during fetching or processing
            _LOGGER.error(
                "Error fetching or processing data from Braiins Pool API: %s", err
            )
            raise UpdateFailed(f"Error updating data: {err}") from err

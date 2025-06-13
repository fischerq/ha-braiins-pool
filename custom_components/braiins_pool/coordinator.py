"""Data update coordinator for the Braiins Pool integration."""

import asyncio
import logging

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta, datetime, timezone

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
        processed_data: dict = {}
        today = datetime.now(timezone.utc).date()

        # Fetch data from all APIs first
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
"""
            user_profile_data = await self.api_client.get_user_profile()
            daily_hashrate_data = await self.api_client.get_daily_hashrate()

            # Fetch block rewards and payouts for the last 7 days
            from_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            to_date = today.strftime("%Y-%m-%d")

            # Fetching block rewards and payouts
            block_rewards_data = await self.api_client.get_block_rewards(from_date, to_date)
            payouts_data = await self.api_client.get_payouts(from_date, to_date)

            processed_data["block_rewards_data"] = block_rewards_data
            workers_data = await self.api_client.get_workers()
            processed_data["workers_data"] = workers_data

            # Process data from fetched endpoints
            processed_data["user_profile_data"] = user_profile_data # Keep raw data as well
            processed_data["daily_hashrate_data"] = daily_hashrate_data # Keep raw data as well
            processed_data["block_rewards_data"] = block_rewards_data # Keep raw data as well
            processed_data["payouts_data"] = payouts_data # Keep raw data as well

            # Extract and process specific data points
            try:
                processed_data["current_balance"] = float(user_profile_data.get("btc", {}).get("current_balance", 0.0))
                processed_data["all_time_reward"] = float(user_profile_data.get("btc", {}).get("all_time_reward", 0.0))
                processed_data["ok_workers"] = int(user_profile_data.get("btc", {}).get("ok_workers", 0))
            except (ValueError, TypeError, KeyError) as e:
                _LOGGER.error("Error parsing user profile data: %s", e)
                # Set default values and continue
                processed_data["current_balance"] = 0.0
                processed_data["all_time_reward"] = 0.0
                processed_data["ok_workers"] = 0

            try:
                 processed_data["pool_5m_hash_rate"] = float(daily_hashrate_data.get("btc", {}).get("pool_5m_hash_rate", 0.0))
            except (ValueError, TypeError, KeyError) as e:
                _LOGGER.error("Error parsing daily hashrate data: %s", e)
                # Set default values and continue
                processed_data["pool_5m_hash_rate"] = 0.0
"""
            return processed_data
        except Exception as err:  # Catch any exception during fetching or processing
            _LOGGER.error(
                "Error fetching or processing data from Braiins Pool API: %s", err
            )
            raise UpdateFailed(f"Error updating data: {err}")

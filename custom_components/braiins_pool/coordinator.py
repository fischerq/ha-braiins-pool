"""Data update coordinator for the Braiins Pool integration."""

import aiohttp
import asyncio
from datetime import timedelta, datetime, timezone
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import logging

from .api import BraiinsPoolApiClient
from .const import (
    DOMAIN,
    CONF_API_KEY,
    SATOSHIS_PER_BTC,
)

_LOGGER = logging.getLogger(__name__)


# Import the actual API client
class BraiinsDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Coordinate updates from the Braiins Pool API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_client: BraiinsPoolApiClient,
        update_interval: timedelta,
    ):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.api_client = api_client

    async def _async_update_data(self) -> dict:
        """Fetch data from the API."""
        _LOGGER.debug("Fetching and processing data for Braiins Pool integration.")
        processed_data: dict = {}
        today = datetime.now(timezone.utc).date()

        try:
            user_profile_data = await self.api_client.get_user_profile()
            processed_data["user_profile_data"] = user_profile_data  # Store raw data

            processed_data["current_balance"] = user_profile_data.get("current_balance", 0.0)
            processed_data["today_reward"] = user_profile_data.get("today_reward", 0.0)
            processed_data["all_time_reward"] = user_profile_data.get("all_time_reward", 0.0)
            processed_data["ok_workers"] = user_profile_data.get("ok_workers", 0)
            processed_data["current_balance_satoshi"] = int(processed_data["current_balance"] * SATOSHIS_PER_BTC)
            processed_data["today_reward_satoshi"] = int(processed_data["today_reward"] * SATOSHIS_PER_BTC)
            processed_data["all_time_reward_satoshi"] = int(processed_data["all_time_reward"] * SATOSHIS_PER_BTC)
            processed_data["pool_5m_hash_rate"] = user_profile_data.get("pool_5m_hash_rate", 0.0)

            return processed_data
        except Exception as err:  # Catch any exception during fetching or processing
            _LOGGER.error(
                "Error fetching or processing data from Braiins Pool API: %s", err
            )
            # Set default values and continue
            processed_data["current_balance"] = 0.0
            processed_data["today_reward"] = 0.0
            processed_data["all_time_reward"] = 0.0
            processed_data["ok_workers"] = 0
            processed_data["current_balance_satoshi"] = 0
            processed_data["today_reward_satoshi"] = 0
            processed_data["all_time_reward_satoshi"] = 0
            processed_data["pool_5m_hash_rate"] = 0.0
            raise UpdateFailed(f"Error updating data: {err}")

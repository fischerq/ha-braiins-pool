"""Data update coordinator for the Braiins Pool integration."""

import asyncio
import logging

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta

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

        try:
            daily_rewards_data = await self.api_client.get_daily_rewards()
            processed_data["today_reward"] = daily_rewards_data

            # Fetch overall stats - assuming this endpoint provides current_balance and all_time_reward
            data = await self.api_client.get_account_stats()

            # Assume 'current_balance' and 'all_time_reward' are at the top level for now
            for key in ["current_balance", "all_time_reward"]:
                value = data.get(key)
                if value is not None:
                    try:
                        processed_data[key] = float(
                            str(value)
                        )  # Convert to string first just in case
                    except ValueError:
                        _LOGGER.warning(
                            "Could not convert %s '%s' to float. Keeping as string.",
                            key,
                            value,
                        )
                        processed_data[key] = value
                else:
                    processed_data[key] = value
            # Note: The data structure for current_balance and all_time_reward needs verification from the other endpoint

            return processed_data
        except Exception as err:  # Catch any exception during fetching or processing
            _LOGGER.error(
                "Error fetching or processing data from Braiins Pool API: %s", err
            )
            raise UpdateFailed(f"Error updating data: {err}") from err

"""The Braiins Pool integration."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .coordinator import BraiinsDataUpdateCoordinator
from .api import BraiinsPoolApiClient
from .const import DOMAIN, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=15)  # Define an update interval


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Braiins Pool from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    api_key = entry.data[CONF_API_KEY]

    session = async_get_clientsession(hass)
    api_client = BraiinsPoolApiClient(api_key, session)

    coordinator = BraiinsDataUpdateCoordinator(
        hass,
        api_client=api_client,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward the setup to the sensor platform
    # Ensure this is done *after* the coordinator is stored
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
"""The Braiins Pool integration."""

# This is the main file for the integration setup.
# It will handle loading and unloading the integration,
# creating the data update coordinator, and forwarding
# setup to the sensor platform.

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Braiins Pool from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    return unload_ok
"""Sensor entities for the Braiins Pool integration."""
import logging

from homeassistant.components.sensor import (
 SensorDeviceClass,
 SensorEntity,
 SensorEntityDescription,
 SensorStateClass,
)
from homeassistant.const import CURRENCY_BITCOIN
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BraiinsDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
 SensorEntityDescription(
 key="today_reward",
 name="Braiins Pool Today's Reward",
 icon="mdi:bitcoin",
 native_unit_of_measurement=CURRENCY_BITCOIN,
 state_class=SensorStateClass.TOTAL_INCREASING,
 device_class=SensorDeviceClass.MONETARY,
 ),
 SensorEntityDescription(
 key="current_balance",
 name="Braiins Pool Current Balance",
 icon="mdi:wallet-outline",
 native_unit_of_measurement=CURRENCY_BITCOIN,
 state_class=SensorStateClass.MEASUREMENT,
 device_class=SensorDeviceClass.MONETARY,
 ),
 SensorEntityDescription(
 key="all_time_reward",
 name="Braiins Pool All Time Reward",
 icon="mdi:medal-outline",
 native_unit_of_measurement=CURRENCY_BITCOIN,
 state_class=SensorStateClass.TOTAL_INCREASING,
 device_class=SensorDeviceClass.MONETARY,
 ),
)


async def async_setup_entry(hass, config_entry, async_add_entities):
 """Set up the sensor platform."""
 coordinator: BraiinsDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

 entities = [
 BraiinsPoolSensor(coordinator, description, config_entry.entry_id)
 for description in SENSOR_TYPES
 ]

 async_add_entities(entities)


class BraiinsPoolSensor(CoordinatorEntity, SensorEntity):
 """Representation of a Braiins Pool sensor."""

 def __init__(self, coordinator, entity_description, entry_id):
 """Initialize the sensor."""
 super().__init__(coordinator)
 self._attr_name = f"{entity_description.name}"
 self.entity_description = entity_description
 self._attr_unique_id = f"{entry_id}_{self.entity_description.key}"

 @property
 def native_value(self):
 """Return the state of the sensor."""
 """Return the state of the sensor, handling potential missing data."""
 return self.coordinator.data.get(self.entity_description.key, None)
"""Sensor entities for the Braiins Pool integration."""1l
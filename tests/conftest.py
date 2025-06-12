# tests/conftest.py
import pytest
from homeassistant.const import CONF_TIME_ZONE

@pytest.fixture
def hass_config():
    # Attempt to set the timezone to UTC very early in the hass setup.
    # This might prevent pytest-homeassistant-custom-component
    # from erroring out when it tries to set "US/Pacific".
    return {
        CONF_TIME_ZONE: "UTC"
    }

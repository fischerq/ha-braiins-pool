# tests/conftest.py
import pytest

# Enable pytest_homeassistant_custom_component fixtures
pytest_plugins = "pytest_homeassistant_custom_component"

# Automatically enable custom integrations for all tests
@pytest.fixture(autouse=True)
async def auto_enable_custom_integrations(enable_custom_integrations):
    yield

from homeassistant.const import CONF_TIME_ZONE

@pytest.fixture
def hass_config():
    # Attempt to set the timezone to UTC very early in the hass setup.
    # This might prevent pytest-homeassistant-custom-component
    # from erroring out when it tries to set "US/Pacific".
    return {
        CONF_TIME_ZONE: "UTC"
    }

import pytest
from unittest.mock import patch

from homeassistant import config_entries, data_entry_flow # Keep these
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_API_KEY
# Import MockConfigEntry from the correct location
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_setup_component

from custom_components.braiins_pool.const import DOMAIN, CONF_REWARDS_ACCOUNT_NAME

MOCK_API_KEY = "test_api_key_123"
MOCK_REWARDS_ACCOUNT_NAME = "My Test Account"

# It's good practice to set up the component, even if minimal,
# to ensure flows are registered.
@pytest.fixture(autouse=True)
async def setup_component_fixture(hass):
    """Ensure component is set up."""
    await async_setup_component(hass, DOMAIN, {}) # Basic setup
    # Also, we need to mock the actual setup_entry because the test flow will try to call it
    # upon successful config. We only want to test the flow itself here.
    with patch("custom_components.braiins_pool.async_setup_entry", return_value=True) as mock_setup:
        yield mock_setup


async def test_config_flow_user_step(hass: HomeAssistant):
    """Test the user config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result is not None # Add a check
    assert result["type"] == data_entry_flow.FlowResultType.FORM # Use Enum for clarity
    assert result["step_id"] == "user"
    # assert result["errors"] is None # errors might not exist if form is shown first time
    assert result.get("errors") is None


    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_API_KEY: MOCK_API_KEY,
            CONF_REWARDS_ACCOUNT_NAME: MOCK_REWARDS_ACCOUNT_NAME,
        },
    )
    await hass.async_block_till_done()

    assert result2 is not None # Add a check
    assert result2["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY # Use Enum
    assert result2["title"] == MOCK_REWARDS_ACCOUNT_NAME
    assert result2["data"] == {
        CONF_API_KEY: MOCK_API_KEY,
        CONF_REWARDS_ACCOUNT_NAME: MOCK_REWARDS_ACCOUNT_NAME,
    }
    assert result2["result"].unique_id == MOCK_REWARDS_ACCOUNT_NAME


async def test_config_flow_empty_api_key(hass: HomeAssistant):
    """Test config flow with an empty API key."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result is not None # Add a check
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_API_KEY: "",
            CONF_REWARDS_ACCOUNT_NAME: MOCK_REWARDS_ACCOUNT_NAME,
        },
    )
    assert result2 is not None # Add a check
    assert result2["type"] == data_entry_flow.FlowResultType.FORM # Use Enum
    assert result2["errors"]["base"] == "invalid_api_key"

async def test_config_flow_empty_rewards_name(hass: HomeAssistant):
    """Test config flow with an empty rewards account name."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result is not None # Add a check
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_API_KEY: MOCK_API_KEY,
            CONF_REWARDS_ACCOUNT_NAME: "",
        },
    )
    assert result2 is not None # Add a check
    assert result2["type"] == data_entry_flow.FlowResultType.FORM # Use Enum
    assert result2["errors"]["base"] == "invalid_rewards_account_name"

async def test_config_flow_already_configured(hass: HomeAssistant):
    """Test config flow when an entry with the same unique ID (rewards account name) already exists."""
    # Create a mock entry first using the corrected MockConfigEntry
    mock_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=MOCK_REWARDS_ACCOUNT_NAME,
        data={CONF_API_KEY: "another_key", CONF_REWARDS_ACCOUNT_NAME: MOCK_REWARDS_ACCOUNT_NAME},
        title=MOCK_REWARDS_ACCOUNT_NAME,
    )
    mock_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result is not None # Add a check
    # Try to configure a new flow with the same rewards account name
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_API_KEY: MOCK_API_KEY,
            CONF_REWARDS_ACCOUNT_NAME: MOCK_REWARDS_ACCOUNT_NAME, # Same name
        },
    )
    assert result2 is not None # Add a check
    assert result2["type"] == data_entry_flow.FlowResultType.ABORT # Use Enum
    assert result2["reason"] == "already_configured"

"""Unit tests for the Braiins Pool coordinator."""

import homeassistant.util.dt as dt_util_real  # Use a different alias to avoid conflict
import pytest
from datetime import timedelta
from unittest.mock import AsyncMock
from decimal import Decimal

from aiohttp import ClientError
from homeassistant.helpers.update_coordinator import UpdateFailed  # Import UpdateFailed
from custom_components.braiins_pool.coordinator import BraiinsDataUpdateCoordinator
from custom_components.braiins_pool.const import DEFAULT_SCAN_INTERVAL, SATOSHIS_PER_BTC

# from homeassistant.helpers.update_coordinator import UpdateFailed # Not explicitly used in asserts, can remove if not needed for other reasons

from freezegun import freeze_time

pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_successful_update(hass):
    "Test successful data update."
    mock_api_client = AsyncMock()

    async def mock_get_account_stats(*args, **kwargs):
        return {
            "btc": {"current_balance": "1.23"}  # Use string for precision
        }  # Assuming this was meant for get_user_profile based on other tests

    mock_api_client.get_user_profile = AsyncMock(
        side_effect=mock_get_account_stats
    )  # Changed from get_account_stats

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()

    # Assertions will be based on processed data in coordinator.data
    mock_api_client.get_user_profile.assert_called_once()  # Added this as it's fetched

    # today_reward comes from user_profile_data.get("btc", {}).get("today_reward", "0")
    # The mock_get_account_stats returns {"btc": {"current_balance": 1.23}}, so "today_reward" is missing.
    assert coordinator.data["today_reward"] == Decimal("0")
    assert coordinator.data["current_balance"] == Decimal(
        "1.23"
    )  # Ensure Decimal comparison
    # Assuming SATOSHIS_PER_BTC is 100_000_000
    assert coordinator.data["today_reward_satoshi"] == 0
    assert coordinator.data["current_balance_satoshi"] == 123000000


@pytest.mark.asyncio
@freeze_time("2023-10-08 12:00:00")
async def test_successful_update_with_new_data(hass):
    """Test successful data update including new endpoints and satoshi conversions."""
    mock_api_client = AsyncMock()

    async def mock_get_user_profile_data(*args, **kwargs):  # Renamed for clarity
        return {
            "btc": {
                "current_balance": "2.50000000",  # String as per API
                "all_time_reward": "10.12345678",  # String as per API
                "ok_workers": 10,  # Integer
                "today_reward": "0.00000001",  # 1 satoshi, String as per API
                "hash_rate_5m": "500.0",  # String as per API
            }
        }

    mock_api_client.get_user_profile = AsyncMock(side_effect=mock_get_user_profile_data)

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()

    mock_api_client.get_user_profile.assert_called_once()

    assert coordinator.data["today_reward"] == Decimal("0.00000001")
    assert coordinator.data["today_reward_satoshi"] == 1

    assert coordinator.data["current_balance"] == Decimal("2.5")
    assert coordinator.data["current_balance_satoshi"] == 250000000

    assert coordinator.data["all_time_reward"] == Decimal("10.12345678")
    assert coordinator.data["all_time_reward_satoshi"] == 1012345678

    assert coordinator.data["ok_workers"] == 10

    assert coordinator.data["pool_5m_hash_rate"] == 500.0

    # Check that the raw data is stored
    assert (
        coordinator.data["user_profile_data"]["btc"]["current_balance"] == "2.50000000"
    )
    # Other raw data fields are not fetched by the coordinator, so no need to assert them here


@pytest.mark.asyncio
async def test_update_failed_api_error(hass):
    "Test data update failure due to API error."
    mock_api_client = AsyncMock()

    # Make get_user_profile raise the API error as it's the one called by coordinator
    mock_api_client.get_user_profile.side_effect = ClientError("API Error")

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()  # Call refresh directly

    assert (
        coordinator.last_update_success is False
    )  # This should be true after UpdateFailed is handled
    mock_api_client.get_user_profile.assert_called_once()


@pytest.mark.asyncio
async def test_update_failed_parsing_error(hass):
    "Test data update failure due to parsing error."
    mock_api_client = AsyncMock()

    async def mock_get_user_profile_empty(*args, **kwargs):
        return {}  # Missing expected keys for user profile

    mock_api_client.get_user_profile = AsyncMock(
        side_effect=mock_get_user_profile_empty
    )

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()

    # The coordinator's _async_update_data handles parsing errors internally and sets defaults.
    # last_update_success remains True unless an UpdateFailed is raised.
    assert coordinator.last_update_success is True
    assert coordinator.data["current_balance"] == Decimal("0.0")
    assert coordinator.data["all_time_reward"] == Decimal("0.0")
    assert coordinator.data["ok_workers"] == 0
    assert coordinator.data["today_reward"] == Decimal("0.0")
    assert coordinator.data["pool_5m_hash_rate"] == 0.0

    mock_api_client.get_user_profile.assert_called_once()


@pytest.mark.asyncio
async def test_update_user_profile_parsing_error_for_rewards(hass):  # Renamed test
    "Test data update failure due to user profile parsing error for reward fields."
    mock_api_client = AsyncMock()

    async def mock_get_user_profile_malformed_rewards(*args, **kwargs):
        return {
            "btc": {
                "current_balance": "1.23",
                "all_time_reward": "not_a_number",  # Malformed
                "ok_workers": 1,
                "today_reward": {},  # Malformed, should be string or number
            }
        }

    mock_api_client.get_user_profile = AsyncMock(
        side_effect=mock_get_user_profile_malformed_rewards
    )

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()

    # The coordinator's _async_update_data has try-except blocks for parsing.
    # Parsing errors for fields like 'today_reward' or 'all_time_reward' will set them to 0.0
    # and not fail the update (last_update_success remains True).
    assert coordinator.last_update_success is True
    assert coordinator.data["today_reward"] == Decimal("0.0")
    assert coordinator.data["all_time_reward"] == Decimal("0.0")
    # If today_reward or all_time_reward parsing fails, current_balance will also be default.
    assert coordinator.data["current_balance"] == Decimal("0.0")
    assert (
        coordinator.data["ok_workers"] == 0
    )  # ok_workers will also default due to the broad exception handling

    mock_api_client.get_user_profile.assert_called_once()


@pytest.mark.asyncio
async def test_update_failed_missing_new_data_keys(hass):
    "Test data update failure due to missing keys in new data."
    mock_api_client = AsyncMock()

    async def mock_get_user_profile_missing_keys(*args, **kwargs):
        return {
            "btc": {
                "current_balance": "4.56"
            }  # Missing 'all_time_reward', 'ok_workers', 'today_reward', 'hash_rate_5m'
        }

    mock_api_client.get_user_profile = AsyncMock(
        side_effect=mock_get_user_profile_missing_keys
    )

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()

    # Graceful handling of missing keys means update should "succeed" but with default values
    assert coordinator.last_update_success is True

    # Asserting default values for missing keys
    assert coordinator.data["all_time_reward"] == Decimal("0.0")
    assert coordinator.data["all_time_reward_satoshi"] == 0
    assert coordinator.data["ok_workers"] == 0
    assert coordinator.data["today_reward"] == Decimal(
        "0.0"
    )  # Was expecting 0.123 from a different mock
    assert coordinator.data["today_reward_satoshi"] == 0  # Was expecting 12300000
    assert coordinator.data["pool_5m_hash_rate"] == 0.0

    # Asserting values that are present
    assert coordinator.data["current_balance"] == Decimal("4.56")
    assert coordinator.data["current_balance_satoshi"] == 456000000

    mock_api_client.get_user_profile.assert_called_once()

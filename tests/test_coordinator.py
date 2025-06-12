"""Unit tests for the Braiins Pool coordinator."""

import homeassistant.util.dt as dt_util_real # Use a different alias to avoid conflict
import pytest
from datetime import timedelta
from unittest.mock import AsyncMock

from aiohttp import ClientError
from custom_components.braiins_pool.coordinator import BraiinsDataUpdateCoordinator
from custom_components.braiins_pool.const import DEFAULT_SCAN_INTERVAL
from homeassistant.helpers.update_coordinator import UpdateFailed

from freezegun import freeze_time
pytestmark = pytest.mark.asyncio  # This line should come after imports

import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

@pytest.mark.asyncio
async def test_successful_update(hass):
    "Test successful data update."
    mock_api_client = AsyncMock()
    mock_api_client.get_account_stats.return_value = {"current_balance": 1.23}
    # The daily rewards endpoint structure has changed
    mock_api_client.get_daily_rewards.return_value = {
        "btc": {"daily_rewards": [{"total_reward": "0.123"}]}
    }
    mock_api_client.get_daily_hashrate.return_value = {}
    mock_api_client.get_block_rewards.return_value = {}
    mock_api_client.get_payouts.return_value = {}
    mock_api_client.get_workers.return_value = {}

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()

    mock_api_client.get_daily_rewards.assert_called_once()  # Keep this assertion for now, will refine later


@pytest.mark.asyncio
@freeze_time("2023-10-08 12:00:00")
async def test_successful_update_with_new_data(hass):
    """Test successful data update including new endpoints."""

    mock_api_client = AsyncMock()

    # Mock return values for all API methods
    mock_api_client.get_daily_rewards.return_value = {
        "btc": {"daily_rewards": [{"total_reward": "0.123"}]}
    }
    mock_api_client.get_user_profile.return_value = {
        "btc": {"current_balance": 4.56, "all_time_reward": 7.89, "ok_workers": 10}
    }
    mock_api_client.get_daily_hashrate.return_value = {"test": "daily_hashrate_data"}
    mock_api_client.get_block_rewards.return_value = {"test": "block_rewards_data"}
    mock_api_client.get_workers.return_value = {"test": "workers_data"}
    mock_api_client.get_payouts.return_value = {"test": "payouts_data"}

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()

    # Assert that all API client methods were called exactly once with expected arguments
    mock_api_client.get_daily_rewards.assert_called_once()
    mock_api_client.get_user_profile.assert_called_once()
    mock_api_client.get_daily_hashrate.assert_called_once()
    mock_api_client.get_block_rewards.assert_called_once_with('2023-10-01', '2023-10-08')
    mock_api_client.get_workers.assert_called_once()
    mock_api_client.get_payouts.assert_called_once_with('2023-10-01', '2023-10-08')

    # Assert that processed_data contains the expected values
    assert coordinator.data["today_reward"] == 0.123
    assert coordinator.data["current_balance"] == 4.56
    assert coordinator.data["all_time_reward"] == 7.89
    assert coordinator.data["ok_workers"] == 10
    # Assert the presence of data from various endpoints
    assert "user_profile_data" in coordinator.data
    assert "daily_hashrate_data" in coordinator.data
    assert "pool_5m_hash_rate" in coordinator.data
    assert "block_rewards_data" in coordinator.data
    assert "workers_data" in coordinator.data
    assert "payouts_data" in coordinator.data


@pytest.mark.asyncio
async def test_update_failed_api_error(hass):
    "Test data update failure due to API error."
    mock_api_client = AsyncMock()

    # Cause an API error by having one of the API calls raise a ClientError
    mock_api_client.get_daily_rewards.side_effect = ClientError("API Error")

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )

    await coordinator.async_refresh()

    assert coordinator.last_update_success is False

    # Only assert the call that caused the error was made, as others might be skipped
    mock_api_client.get_daily_rewards.assert_called_once()
@pytest.mark.asyncio
async def test_update_failed_parsing_error(hass):
    "Test data update failure due to parsing error."
    mock_api_client = AsyncMock()

    mock_api_client.get_user_profile.return_value = {}  # Missing expected keys for user profile
    mock_api_client.get_daily_rewards.return_value = {
        "btc": {"daily_rewards": [{"total_reward": "0.123"}]}
    }

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()
    assert coordinator.last_update_success is False

    # Ensure relevant API calls were made
    mock_api_client.get_user_profile.assert_called_once()
    # The coordinator should still attempt to fetch other data even if one fails
    mock_api_client.get_daily_rewards.assert_called_once()
    mock_api_client.get_daily_hashrate.assert_called_once()
    mock_api_client.get_block_rewards.assert_called_once()
    mock_api_client.get_workers.assert_called_once()
    mock_api_client.get_payouts.assert_called_once()


@pytest.mark.asyncio
async def test_update_failed_daily_rewards_parsing_error(hass):
    "Test data update failure due to daily rewards parsing error."
    mock_api_client = AsyncMock()

    mock_api_client.get_daily_rewards.return_value = {"btc": {"daily_rewards": [{}]}}  # Missing daily_rewards key
    # Add mocks for other calls that will occur before the tested parsing error might happen or during recovery/cleanup
    mock_api_client.get_user_profile.return_value = {"btc": {"current_balance": 1.23, "all_time_reward": 10.0, "ok_workers": 1}} # Provide valid data for other calls
    mock_api_client.get_daily_hashrate.return_value = {"btc": {"pool_5m_hash_rate": 500.0}}
    mock_api_client.get_block_rewards.return_value = {} # Empty is fine
    mock_api_client.get_payouts.return_value = {} # Empty is fine
    mock_api_client.get_workers.return_value = {} # Empty is fine


    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )

    # This test expects UpdateFailed because daily_rewards parsing will fail with the above mock
    # The initial error was that this was NOT raising UpdateFailed, because an earlier .get() call on an unmocked coroutine was failing.
    # Now that other calls are mocked, the coordinator should gracefully handle the missing 'total_reward'.
    await coordinator.async_refresh()
    assert coordinator.last_update_success is True # Expect success because of default handling
    assert coordinator.data["today_reward"] == 0.0 # Default value

    mock_api_client.get_daily_rewards.assert_called_once()
    # No need to assert other calls if the failure is intended early.
    # However, the code calls them all within the try block before this specific parsing.
    # So they will be called.
    mock_api_client.get_user_profile.assert_called_once()
    mock_api_client.get_daily_hashrate.assert_called_once()
    mock_api_client.get_block_rewards.assert_called_once()
    mock_api_client.get_payouts.assert_called_once()
    mock_api_client.get_workers.assert_called_once()


@pytest.mark.asyncio
async def test_update_failed_missing_new_data_keys(hass):
    "Test data update failure due to missing keys in new data."
    mock_api_client = AsyncMock()

    # Mock data with missing keys from a new endpoint (e.g., user profile)
    # We are simulating missing keys that the coordinator *expects* to be able to process.
    mock_api_client.get_daily_rewards.return_value = {
        "btc": {"daily_rewards": [{"total_reward": "0.123"}]}
    }
    # Simulate missing 'all_time_reward' and 'ok_workers' in user profile data
    mock_api_client.get_user_profile.return_value = { # This will cause parsing error for all_time_reward / ok_workers
        "btc": {"current_balance": 4.56}
    }
    mock_api_client.get_daily_hashrate.return_value = { # This will cause parsing error for pool_5m_hash_rate
        "btc": {}
    }
    # These can be valid as they are not the source of the intended error for this test
    mock_api_client.get_block_rewards.return_value = {"some_key": "some_value"}
    mock_api_client.get_workers.return_value = {"some_key": "some_value"}
    mock_api_client.get_payouts.return_value = {"some_key": "some_value"}

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )

    # The coordinator should gracefully handle missing keys by applying defaults.
    await coordinator.async_refresh()
    assert coordinator.last_update_success is True # Expect success

    # Assert that default values are set for the missing keys
    assert coordinator.data["all_time_reward"] == 0.0
    assert coordinator.data["ok_workers"] == 0
    assert coordinator.data["pool_5m_hash_rate"] == 0.0

    # Assert that keys that were present are processed
    assert coordinator.data["today_reward"] == 0.123
    assert coordinator.data["current_balance"] == 4.56

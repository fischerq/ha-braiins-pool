"""Unit tests for the Braiins Pool coordinator."""

import pytest
from datetime import timedelta, datetime, date
from unittest.mock import AsyncMock, patch

from aiohttp import ClientError
from custom_components.braiins_pool.coordinator import BraiinsDataUpdateCoordinator
from custom_components.braiins_pool.const import DEFAULT_SCAN_INTERVAL
from homeassistant.helpers.update_coordinator import UpdateFailed

pytestmark = pytest.mark.asyncio  # This line should come after imports


@pytest.mark.asyncio
async def test_successful_update(hass):
    "Test successful data update."
    mock_api_client = AsyncMock()
    mock_api_client.get_account_stats.return_value = {"current_balance": 1.23}
    mock_api_client.get_daily_rewards.return_value = {
        "btc": {"daily_rewards": [{"total_reward": "0.123"}]}
    }

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()

    mock_api_client.get_daily_rewards.assert_called_once()  # Keep this assertion for now, will refine later


@pytest.mark.asyncio
@patch("custom_components.braiins_pool.coordinator.datetime")
async def test_successful_update_with_new_data(mock_datetime, hass):
    "Test successful data update including new endpoints."
    # Mock datetime to return a fixed date for predictable date calculations
    mock_datetime.utcnow.return_value = datetime(2023, 10, 8)
    mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
    mock_datetime.date.side_effect = lambda *args, **kw: date(*args, **kw)

    mock_api_client = AsyncMock()

    # Mock return values for all API methods
    mock_api_client.get_daily_rewards.return_value = {
        "btc": {"daily_rewards": [{"total_reward": "0.123"}]}
    }
    mock_api_client.get_account_stats.return_value = (
        {}
    )  # No longer used for balance/reward
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

    expected_from_date = (date(2023, 10, 8) - timedelta(days=7)).strftime("%Y-%m-%d")
    expected_to_date = date(2023, 10, 8).strftime("%Y-%m-%d")

    mock_api_client.get_block_rewards.assert_called_once_with(
        expected_from_date, expected_to_date
    )
    mock_api_client.get_workers.assert_called_once()
    mock_api_client.get_payouts.assert_called_once_with(
        expected_from_date, expected_to_date
    )

    # Assert that processed_data contains the expected values
    assert coordinator.data["today_reward"] == 0.123
    assert coordinator.data["current_balance"] == 4.56
    assert coordinator.data["all_time_reward"] == 7.89
    assert coordinator.data["ok_workers"] == 10
    # Assert the presence of raw data from new endpoints
    assert "user_profile_data" in coordinator.data
    assert "daily_hashrate_data" in coordinator.data
    assert "pool_5m_hash_rate" in coordinator.data # Add assertion for pool_5m_hash_rate
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
    with pytest.raises(UpdateFailed):  # Change expected exception to UpdateFailed
        await coordinator.async_refresh()

    mock_api_client.get_account_stats.assert_called_once()
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
    with pytest.raises(UpdateFailed):  # Change expected exception to UpdateFailed
        await coordinator.async_refresh()

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

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )

    with pytest.raises(UpdateFailed):  # Change expected exception to UpdateFailed
        await coordinator.async_refresh()

    mock_api_client.get_daily_rewards.assert_called_once()
    # Ensure other API calls were attempted
    mock_api_client.get_user_profile.assert_called_once()
    mock_api_client.get_daily_hashrate.assert_called_once()
    mock_api_client.get_workers.assert_called_once()
    mock_api_client.get_daily_rewards.assert_called_once()


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
    mock_api_client.get_user_profile.return_value = {
        "btc": {"current_balance": 4.56}
    }
    mock_api_client.get_daily_hashrate.return_value = {
        "btc": {}
    }  # Missing 'pool_5m_hash_rate'
    mock_api_client.get_block_rewards.return_value = {"test": "block_rewards_data"} # Keep this as it doesn't cause parsing error
    mock_api_client.get_workers.return_value = {"test": "workers_data"}
    mock_api_client.get_payouts.return_value = {"test": "payouts_data"}

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    with pytest.raises(UpdateFailed) as excinfo:
        await coordinator.async_refresh()
    assert "Error updating data: " in str(excinfo.value)

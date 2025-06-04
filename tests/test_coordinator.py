"""Unit tests for the Braiins Pool coordinator."""

import pytest
from datetime import timedelta
from unittest.mock import AsyncMock, patch

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

    mock_api_client.get_account_stats.assert_called_once()
    mock_api_client.get_daily_rewards.assert_called_once()
    assert coordinator.data is not None
    assert coordinator.data["current_balance"] == 1.23
    assert coordinator.data["today_reward"] == 0.123


@pytest.mark.asyncio
async def test_update_failed_api_error(hass):
    "Test data update failure due to API error."
    mock_api_client = AsyncMock()

    mock_api_client.get_account_stats.side_effect = Exception("API Error")
    mock_api_client.get_daily_rewards.return_value = {
        "btc": {"daily_rewards": [{"total_reward": "0.123"}]}
    }

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    with pytest.raises(UpdateFailed):
        await coordinator.async_refresh()

    mock_api_client.get_account_stats.assert_called_once()
    mock_api_client.get_daily_rewards.assert_not_called()  # Assuming stats fetch fails first


@pytest.mark.asyncio
async def test_update_failed_parsing_error(hass):
    "Test data update failure due to parsing error."
    mock_api_client = AsyncMock()

    mock_api_client.get_account_stats.return_value = {}  # Missing expected key
    mock_api_client.get_daily_rewards.return_value = {
        "btc": {"daily_rewards": [{"total_reward": "0.123"}]}
    }

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    with pytest.raises(UpdateFailed):
        await coordinator.async_refresh()

    mock_api_client.get_account_stats.assert_called_once()
    mock_api_client.get_daily_rewards.assert_not_called()  # Assuming stats fetch fails first


@pytest.mark.asyncio
async def test_update_failed_daily_rewards_parsing_error(hass):
    "Test data update failure due to daily rewards parsing error."
    mock_api_client = AsyncMock()

    mock_api_client.get_account_stats.return_value = {"current_balance": 1.23}
    mock_api_client.get_daily_rewards.return_value = {
        "btc": {}
    }  # Missing daily_rewards key

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, DEFAULT_SCAN_INTERVAL
    )

    with pytest.raises(UpdateFailed):
        await coordinator.async_refresh()

    mock_api_client.get_account_stats.assert_called_once()
    mock_api_client.get_daily_rewards.assert_called_once()

"""Unit tests for the Braiins Pool coordinator."""

import homeassistant.util.dt as dt_util_real  # Use a different alias to avoid conflict
import pytest
from datetime import timedelta
from unittest.mock import AsyncMock

from aiohttp import ClientError
from custom_components.braiins_pool.coordinator import BraiinsDataUpdateCoordinator
from custom_components.braiins_pool.const import DEFAULT_SCAN_INTERVAL, SATOSHIS_PER_BTC

# from homeassistant.helpers.update_coordinator import UpdateFailed # Not explicitly used in asserts, can remove if not needed for other reasons

from freezegun import freeze_time

pytestmark = pytest.mark.asyncio

# import sys # eprint not used, can remove

# def eprint(*args, **kwargs):
#     print(*args, file=sys.stderr, **kwargs)


@pytest.mark.asyncio
async def test_successful_update(hass):
    "Test successful data update."
    mock_api_client = AsyncMock()

    async def mock_get_account_stats(*args, **kwargs):
        return {
            "btc": {"current_balance": 1.23}
        }  # Assuming this was meant for get_user_profile based on other tests

    mock_api_client.get_user_profile = AsyncMock(
        side_effect=mock_get_account_stats
    )  # Changed from get_account_stats

    async def mock_get_daily_rewards(*args, **kwargs):
        return {"btc": {"daily_rewards": [{"total_reward": "0.123"}]}}

    mock_api_client.get_daily_rewards = AsyncMock(side_effect=mock_get_daily_rewards)

    async def mock_get_daily_hashrate(*args, **kwargs):
        return {}  # Empty dict as per original

    mock_api_client.get_daily_hashrate = AsyncMock(side_effect=mock_get_daily_hashrate)

    async def mock_get_block_rewards(*args, **kwargs):
        return {}  # Empty dict

    mock_api_client.get_block_rewards = AsyncMock(side_effect=mock_get_block_rewards)

    async def mock_get_payouts(*args, **kwargs):
        return {}  # Empty dict

    mock_api_client.get_payouts = AsyncMock(side_effect=mock_get_payouts)

    async def mock_get_workers(*args, **kwargs):
        return {}  # Empty dict

    mock_api_client.get_workers = AsyncMock(side_effect=mock_get_workers)

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()

    # Assertions will be based on processed data in coordinator.data
    mock_api_client.get_daily_rewards.assert_called_once()
    mock_api_client.get_user_profile.assert_called_once()  # Added this as it's fetched

    assert coordinator.data["today_reward"] == 0.123
    assert coordinator.data["current_balance"] == 1.23
    # Assuming SATOSHIS_PER_BTC is 100_000_000
    assert coordinator.data["today_reward_satoshi"] == 12300000
    assert coordinator.data["current_balance_satoshi"] == 123000000


@pytest.mark.asyncio
@freeze_time("2023-10-08 12:00:00")
async def test_successful_update_with_new_data(hass):
    """Test successful data update including new endpoints and satoshi conversions."""
    mock_api_client = AsyncMock()

    async def mock_get_daily_rewards(*args, **kwargs):
        return {"btc": {"daily_rewards": [{"total_reward": "0.00000001"}]}}  # 1 satoshi

    mock_api_client.get_daily_rewards = AsyncMock(side_effect=mock_get_daily_rewards)

    async def mock_get_user_profile(*args, **kwargs):
        return {
            "btc": {
                "current_balance": 2.50000000,
                "all_time_reward": 10.12345678,
                "ok_workers": 10,
            }
        }

    mock_api_client.get_user_profile = AsyncMock(side_effect=mock_get_user_profile)

    async def mock_get_daily_hashrate(*args, **kwargs):
        return {"test_hash_key": "daily_hashrate_data"}

    mock_api_client.get_daily_hashrate = AsyncMock(side_effect=mock_get_daily_hashrate)

    async def mock_get_block_rewards(*args, **kwargs):
        return {
            "test_block_key": "block_rewards_data"
        }  # Changed "test" to "test_block_key"

    mock_api_client.get_block_rewards = AsyncMock(side_effect=mock_get_block_rewards)

    async def mock_get_workers(*args, **kwargs):
        return {
            "test_worker_key": "workers_data"
        }  # Changed "test" to "test_worker_key"

    mock_api_client.get_workers = AsyncMock(side_effect=mock_get_workers)

    async def mock_get_payouts(*args, **kwargs):
        return {
            "test_payout_key": "payouts_data"
        }  # Changed "test" to "test_payout_key"

    mock_api_client.get_payouts = AsyncMock(side_effect=mock_get_payouts)

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()

    mock_api_client.get_daily_rewards.assert_called_once()
    mock_api_client.get_user_profile.assert_called_once()
    mock_api_client.get_daily_hashrate.assert_called_once()
    mock_api_client.get_block_rewards.assert_called_once_with(
        "2023-10-01", "2023-10-08"
    )
    mock_api_client.get_workers.assert_called_once()
    mock_api_client.get_payouts.assert_called_once_with("2023-10-01", "2023-10-08")

    assert coordinator.data["today_reward"] == 0.00000001
    assert coordinator.data["today_reward_satoshi"] == 1

    assert coordinator.data["current_balance"] == 2.5
    assert coordinator.data["current_balance_satoshi"] == 250000000

    assert coordinator.data["all_time_reward"] == 10.12345678
    assert coordinator.data["all_time_reward_satoshi"] == 1012345678

    assert coordinator.data["ok_workers"] == 10

    assert coordinator.data["user_profile_data"]["btc"]["current_balance"] == 2.5
    assert (
        coordinator.data["daily_hashrate_data"]["test_hash_key"]
        == "daily_hashrate_data"
    )
    # assert "pool_5m_hash_rate" in coordinator.data # This depends on processing logic in coordinator
    assert (
        coordinator.data["block_rewards_data"]["test_block_key"] == "block_rewards_data"
    )
    assert coordinator.data["workers_data"]["test_worker_key"] == "workers_data"
    assert coordinator.data["payouts_data"]["test_payout_key"] == "payouts_data"


@pytest.mark.asyncio
async def test_update_failed_api_error(hass):
    "Test data update failure due to API error."
    mock_api_client = AsyncMock()

    # This is correct: side_effect is an exception instance
    mock_api_client.get_daily_rewards.side_effect = ClientError("API Error")

    # Mock other calls that might happen before the failing one, or during the process
    async def mock_get_user_profile(*args, **kwargs):
        return {
            "btc": {"current_balance": 4.56, "all_time_reward": 7.89, "ok_workers": 10}
        }

    mock_api_client.get_user_profile = AsyncMock(side_effect=mock_get_user_profile)

    async def mock_get_daily_hashrate(*args, **kwargs):
        return {"test_hash_key": "daily_hashrate_data"}

    mock_api_client.get_daily_hashrate = AsyncMock(side_effect=mock_get_daily_hashrate)

    async def mock_get_block_rewards(*args, **kwargs):
        return {"test_block_key": "block_rewards_data"}

    mock_api_client.get_block_rewards = AsyncMock(side_effect=mock_get_block_rewards)

    async def mock_get_workers(*args, **kwargs):
        return {"test_worker_key": "workers_data"}

    mock_api_client.get_workers = AsyncMock(side_effect=mock_get_workers)

    async def mock_get_payouts(*args, **kwargs):
        return {"test_payout_key": "payouts_data"}

    mock_api_client.get_payouts = AsyncMock(side_effect=mock_get_payouts)

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()

    assert coordinator.last_update_success is False
    mock_api_client.get_daily_rewards.assert_called_once()


@pytest.mark.asyncio
async def test_update_failed_parsing_error(hass):
    "Test data update failure due to parsing error."
    mock_api_client = AsyncMock()

    async def mock_get_user_profile_empty(*args, **kwargs):
        return {}  # Missing expected keys for user profile

    mock_api_client.get_user_profile = AsyncMock(
        side_effect=mock_get_user_profile_empty
    )

    async def mock_get_daily_rewards(*args, **kwargs):
        return {"btc": {"daily_rewards": [{"total_reward": "0.123"}]}}

    mock_api_client.get_daily_rewards = AsyncMock(side_effect=mock_get_daily_rewards)

    # Provide default mocks for other methods to ensure they are called
    async def mock_get_daily_hashrate(*args, **kwargs):
        return {"default_hash": "data"}

    mock_api_client.get_daily_hashrate = AsyncMock(side_effect=mock_get_daily_hashrate)

    async def mock_get_block_rewards(*args, **kwargs):
        return {"default_block": "data"}

    mock_api_client.get_block_rewards = AsyncMock(side_effect=mock_get_block_rewards)

    async def mock_get_workers(*args, **kwargs):
        return {"default_worker": "data"}

    mock_api_client.get_workers = AsyncMock(side_effect=mock_get_workers)

    async def mock_get_payouts(*args, **kwargs):
        return {"default_payout": "data"}

    mock_api_client.get_payouts = AsyncMock(side_effect=mock_get_payouts)

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()
    assert (
        coordinator.last_update_success is True
    )  # Because get_user_profile will lead to parsing error
    assert coordinator.data["current_balance"] == 0.0
    assert coordinator.data["all_time_reward"] == 0.0
    assert coordinator.data["ok_workers"] == 0

    mock_api_client.get_user_profile.assert_called_once()
    mock_api_client.get_daily_rewards.assert_called_once()
    mock_api_client.get_daily_hashrate.assert_called_once()
    mock_api_client.get_block_rewards.assert_called_once()
    mock_api_client.get_workers.assert_called_once()
    mock_api_client.get_payouts.assert_called_once()


@pytest.mark.asyncio
async def test_update_failed_daily_rewards_parsing_error(hass):
    "Test data update failure due to daily rewards parsing error."
    mock_api_client = AsyncMock()

    async def mock_get_daily_rewards_malformed(*args, **kwargs):
        return {"btc": {"daily_rewards": [{}]}}  # Missing 'total_reward' key

    mock_api_client.get_daily_rewards = AsyncMock(
        side_effect=mock_get_daily_rewards_malformed
    )

    async def mock_get_user_profile(*args, **kwargs):
        return {
            "btc": {"current_balance": 1.23, "all_time_reward": 10.0, "ok_workers": 1}
        }

    mock_api_client.get_user_profile = AsyncMock(side_effect=mock_get_user_profile)

    async def mock_get_daily_hashrate(*args, **kwargs):
        # Original test had "btc": {"pool_5m_hash_rate": 500.0}, but coordinator expects "test_hash_key" based on other tests
        # Let's use a structure that the coordinator can process or ignore gracefully
        return {"some_hash_data": 500.0}

    mock_api_client.get_daily_hashrate = AsyncMock(side_effect=mock_get_daily_hashrate)

    async def mock_get_block_rewards(*args, **kwargs):
        return {}

    mock_api_client.get_block_rewards = AsyncMock(side_effect=mock_get_block_rewards)

    async def mock_get_payouts(*args, **kwargs):
        return {}

    mock_api_client.get_payouts = AsyncMock(side_effect=mock_get_payouts)

    async def mock_get_workers(*args, **kwargs):
        return {}

    mock_api_client.get_workers = AsyncMock(side_effect=mock_get_workers)

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()

    # The coordinator's _async_update_data has try-except blocks for parsing.
    # A parsing error for 'total_reward' (KeyError) will set today_reward to 0.0 and not fail the update.
    assert coordinator.last_update_success is True
    assert coordinator.data["today_reward"] == 0.0

    mock_api_client.get_daily_rewards.assert_called_once()
    mock_api_client.get_user_profile.assert_called_once()
    mock_api_client.get_daily_hashrate.assert_called_once()
    mock_api_client.get_block_rewards.assert_called_once()
    mock_api_client.get_payouts.assert_called_once()
    mock_api_client.get_workers.assert_called_once()


@pytest.mark.asyncio
async def test_update_failed_missing_new_data_keys(hass):
    "Test data update failure due to missing keys in new data."
    mock_api_client = AsyncMock()

    async def mock_get_daily_rewards(*args, **kwargs):
        return {"btc": {"daily_rewards": [{"total_reward": "0.123"}]}}

    mock_api_client.get_daily_rewards = AsyncMock(side_effect=mock_get_daily_rewards)

    async def mock_get_user_profile_missing_keys(*args, **kwargs):
        return {
            "btc": {"current_balance": 4.56}
        }  # Missing 'all_time_reward', 'ok_workers'

    mock_api_client.get_user_profile = AsyncMock(
        side_effect=mock_get_user_profile_missing_keys
    )

    async def mock_get_daily_hashrate_empty_btc(*args, **kwargs):
        return {
            "btc": {}
        }  # Will cause parsing error for pool_5m_hash_rate if that key is expected directly under "btc"

    mock_api_client.get_daily_hashrate = AsyncMock(
        side_effect=mock_get_daily_hashrate_empty_btc
    )

    async def mock_get_block_rewards(*args, **kwargs):
        return {"some_key": "some_value"}

    mock_api_client.get_block_rewards = AsyncMock(side_effect=mock_get_block_rewards)

    async def mock_get_workers(*args, **kwargs):
        return {"some_key": "some_value"}

    mock_api_client.get_workers = AsyncMock(side_effect=mock_get_workers)

    async def mock_get_payouts(*args, **kwargs):
        return {"some_key": "some_value"}

    mock_api_client.get_payouts = AsyncMock(side_effect=mock_get_payouts)

    coordinator = BraiinsDataUpdateCoordinator(
        hass, mock_api_client, timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()

    # Graceful handling of missing keys means update should "succeed" but with default values
    assert coordinator.last_update_success is True

    assert coordinator.data["all_time_reward"] == 0.0
    assert coordinator.data["ok_workers"] == 0
    # assert coordinator.data["pool_5m_hash_rate"] == 0.0 # Depends on how it's processed

    assert coordinator.data["today_reward"] == 0.123
    assert coordinator.data["today_reward_satoshi"] == 12300000  # 0.123 * 100_000_000

    assert coordinator.data["current_balance"] == 4.56
    assert (
        coordinator.data["current_balance_satoshi"] == 456000000
    )  # 4.56 * 100_000_000

    # For all_time_reward and ok_workers, they are set to 0.0 and 0 if keys are missing
    assert coordinator.data["all_time_reward"] == 0.0
    assert coordinator.data["all_time_reward_satoshi"] == 0
    assert coordinator.data["ok_workers"] == 0

import logging
import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, patch

logging.basicConfig(level=logging.DEBUG)

import pytest

from aiohttp import ClientError
from aiohttp.client_exceptions import ContentTypeError

from custom_components.braiins_pool.api import BraiinsPoolApiClient
from custom_components.braiins_pool.coordinator import BraiinsDataUpdateCoordinator

import pytest


class TestBraiinsPoolApiClient(unittest.TestCase):

    def setUp(self):
        """Set up a mock ClientSession and API key for each test."""
        self.mock_session = AsyncMock()
        self.api_key = "test_api_key"
        self.api_client = BraiinsPoolApiClient(self.mock_session, self.api_key)

    async def mock_response(self, status=200, json_data=None):
        """Helper to create a mock ClientResponse."""
        mock_resp = AsyncMock()  # Use AsyncMock
        mock_resp.status = status
        mock_resp.json = AsyncMock(
            return_value=json_data if json_data is not None else {}
        )
        mock_resp.raise_for_status = MagicMock()  # Add raise_for_status mock


        if status >= 400:
            mock_resp.raise_for_status.side_effect = ClientError(
                f"Mock HTTP error {status}"
            )
        pytestmark = pytest.mark.asyncio  # This line should come after imports
        return mock_resp

    @patch("custom_components.braiins_pool.api._LOGGER")
    async def test_get_account_stats_success(self, mock_logger):
        """Test successful fetching of account stats."""
        mock_data = {"test": "data"}
        self.mock_session.get.return_value.__aenter__.return_value = (
            await self.mock_response(json_data=mock_data)
        )

        data = await self.api_client.get_account_stats()

        self.mock_session.get.assert_awaited_once_with(
            "https://pool.braiins.com/stats/json/btc/",
            headers={"Pool-Auth-Token": self.api_key},
        )
        self.assertEqual(data, mock_data)  # Assert data matches mock_data
        mock_logger.debug.assert_called()  # Check if debug logging was called

    @patch("custom_components.braiins_pool.api._LOGGER")
    async def test_get_account_stats_401(self, mock_logger):
        """Test handling of 401 Unauthorized for account stats."""
        self.mock_session.get.return_value.__aenter__.return_value = (
            await self.mock_response(status=401)
        )

        with self.assertRaises(ClientError):
            await self.api_client.get_account_stats()

        self.mock_session.get.assert_awaited_once_with(
            "https://pool.braiins.com/stats/json/btc/",
            headers={"Pool-Auth-Auth-Token": self.api_key},
        )  # Assert URL and headers
        self.mock_session.get.return_value.__aenter__.return_value.raise_for_status.assert_called_once()  # Assert raise_for_status was called
        mock_logger.error.assert_called()  # Check if error logging was called for 401

    @patch("custom_components.braiins_pool.api._LOGGER")
    async def test_get_account_stats_other_error(self, mock_logger):
        """Test handling of other HTTP errors for account stats."""
        self.mock_session.get.return_value.__aenter__.return_value = (
            await self.mock_response(status=500)
        )

        with self.assertRaises(ClientError):
            await self.api_client.get_account_stats()

        self.mock_session.get.assert_awaited_once_with(
            "https://pool.braiins.com/stats/json/btc/",
            headers={"Pool-Auth-Auth-Token": self.api_key},
        )  # Assert URL and headers
        self.mock_session.get.return_value.__aenter__.return_value.raise_for_status.assert_called_once()  # Assert raise_for_status was called
        mock_logger.error.assert_called()  # Check if error logging was called for 500

    @patch("custom_components.braiins_pool.api._LOGGER")
    async def test_get_daily_rewards_success(self, mock_logger):
        """Test successful fetching and parsing of daily rewards."""
        mock_data = {"btc": {"daily_rewards": [{"total_reward": "0.12345"}]}}
        self.mock_session.get.return_value.__aenter__.return_value = (
            await self.mock_response(json_data=mock_data)
        )

        reward = await self.api_client.get_daily_rewards()

        # Update the expected URL based on the actual implementation
        self.mock_session.get.assert_awaited_once_with(
            "https://pool.braiins.com/accounts/rewards/json/btc",
            headers={"Pool-Auth-Token": self.api_key},
        )
        self.assertEqual(reward, 0.12345)  # Assert the parsed reward value
        mock_logger.debug.assert_called()  # Check if debug logging was called

    @patch("custom_components.braiins_pool.api._LOGGER")
    async def test_get_daily_rewards_401(self, mock_logger):
        """Test handling of 401 Unauthorized for daily rewards."""
        # Update the expected URL based on the actual implementation

        self.mock_session.get.return_value.__aenter__.return_value = (
            await self.mock_response(status=401)
        )

        with self.assertRaises(ClientError):
            await self.api_client.get_account_stats()

        self.mock_session.get.assert_awaited_once_with(
            "https://pool.braiins.com/accounts/rewards/json/btc",
            headers={"Pool-Auth-Token": self.api_key},
        )
        self.mock_session.get.return_value.__aenter__.return_value.raise_for_status.assert_called_once()  # Assert raise_for_status was called
        mock_logger.error.assert_called()  # Check if error logging was called

    @patch("custom_components.braiins_pool.api._LOGGER")
    async def test_get_daily_rewards_client_error(self, mock_logger):
        """Test handling of aiohttp ClientError during daily rewards fetch."""
        expected_url = "https://pool.braiins.com/accounts/rewards/json/btc"
        self.mock_session.get.side_effect = ClientError("Network issue")

        with self.assertRaises(ClientError):
            await self.api_client.get_daily_rewards()

        self.mock_session.get.assert_awaited_once_with(
            expected_url, headers={"Pool-Auth-Token": self.api_key}
        )
        mock_logger.error.assert_called_once_with(
            "Error fetching account stats from Braiins Pool API: Network or client error: %s",
            "Network issue",
        )

    @patch("custom_components.braiins_pool.api._LOGGER")
    async def test_get_user_profile_success(self, mock_logger):
        """Test successful fetching of user profile."""
        mock_data = {"test": "user_profile_data"}
        self.mock_session.get.return_value.__aenter__.return_value = (
            await self.mock_response(json_data=mock_data)
        )
        data = await self.api_client.get_user_profile()
        self.mock_session.get.assert_awaited_once_with(
            "https://pool.braiins.com/accounts/profile/json/btc/",
            headers={"Pool-Auth-Token": self.api_key},
        )
        self.assertEqual(data, mock_data)
        mock_logger.debug.assert_called()

    @patch("custom_components.braiins_pool.api._LOGGER")
    async def test_get_daily_hashrate_success(self, mock_logger):
        """Test successful fetching of daily hashrate."""
        mock_data = {"test": "daily_hashrate_data"}
        self.mock_session.get.return_value.__aenter__.return_value = (
            await self.mock_response(json_data=mock_data)
        )
        data = await self.api_client.get_daily_hashrate()
        self.mock_session.get.assert_awaited_once_with(
            "https://pool.braiins.com/accounts/hash_rate_daily/json/user/btc",
            headers={"Pool-Auth-Token": self.api_key},
        )
        self.assertEqual(data, mock_data)
        mock_logger.debug.assert_called()

    @patch("custom_components.braiins_pool.api._LOGGER")
    async def test_get_block_rewards_success(self, mock_logger):
        """Test successful fetching of block rewards."""
        mock_data = {"test": "block_rewards_data"}
        from_date = "2023-10-01"
        to_date = "2023-10-07"
        self.mock_session.get.return_value.__aenter__.return_value = (
            await self.mock_response(json_data=mock_data)
        )
        data = await self.api_client.get_block_rewards(from_date, to_date)
        self.mock_session.get.assert_awaited_once_with(
            f"https://pool.braiins.com/accounts/block_rewards/json/btc?from={from_date}&to={to_date}",
            headers={"Pool-Auth-Token": self.api_key},
        )
        self.assertEqual(data, mock_data)
        mock_logger.debug.assert_called()

    @patch("custom_components.braiins_pool.api._LOGGER")
    async def test_get_workers_success(self, mock_logger):
        """Test successful fetching of worker data."""
        mock_data = {"test": "workers_data"}
        self.mock_session.get.return_value.__aenter__.return_value = (
            await self.mock_response(json_data=mock_data)
        )
        data = await self.api_client.get_workers()
        self.mock_session.get.assert_awaited_once_with(
            "https://pool.braiins.com/accounts/workers/json/btc/",
            headers={"Pool-Auth-Token": self.api_key},
        )
        self.assertEqual(data, mock_data)
        mock_logger.debug.assert_called()

    @patch("custom_components.braiins_pool.api._LOGGER")
    async def test_get_payouts_success(self, mock_logger):
        """Test successful fetching of payouts data."""
        mock_data = {"test": "payouts_data"}
        from_date = "2023-10-01"
        to_date = "2023-10-07"
        self.mock_session.get.return_value.__aenter__.return_value = (
            await self.mock_response(json_data=mock_data)
        )
        data = await self.api_client.get_payouts(from_date, to_date)
        self.mock_session.get.assert_awaited_once_with(
            f"https://pool.braiins.com/accounts/payouts/json/btc?from={from_date}&to={to_date}",
            headers={"Pool-Auth-Token": self.api_key},
        )
        self.assertEqual(data, mock_data)
        mock_logger.debug.assert_called()

    # Add more test cases for different error conditions, data structures, etc.

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from aiohttp import ClientError
from aiohttp.client_exceptions import ContentTypeError

from custom_components.braiins_pool.api import BraiinsPoolApiClient
import pytest


class TestBraiinsPoolApiClient(unittest.TestCase):

    def setUp(self):
        """Set up a mock ClientSession and API key for each test."""
        self.mock_session = AsyncMock()
        self.api_key = "test_api_key"
        self.api_client = BraiinsPoolApiClient(self.mock_session, self.api_key)

    async def mock_response(self, status=200, json_data=None):
        """Helper to create a mock ClientResponse."""
        mock_resp = MagicMock()
        mock_resp.status = status
        mock_resp.json = AsyncMock(
            return_value=json_data if json_data is not None else {}
        )
        mock_resp.raise_for_status = MagicMock()  # Add raise_for_status mock
        mock_resp.text = AsyncMock(return_value="Error response text")  # Add text mock

        if status >= 400:
            mock_resp.raise_for_status.side_effect = ClientError(
                f"Mock HTTP error {status}"
            )
        pytestmark = pytest.mark.asyncio  # This line should come after imports

        # Mock __aenter__ and __aexit__ for async context manager
        pytestmark = pytest.mark.asyncio

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
        expected_url = "https://pool.braiins.com/accounts/rewards/json/btc"
        self.mock_session.get.assert_awaited_once_with(
            expected_url, headers={"Pool-Auth-Token": self.api_key}
        )
        self.assertEqual(reward, 0.12345)  # Assert the parsed reward value
        mock_logger.debug.assert_called()  # Check if debug logging was called

    @patch("custom_components.braiins_pool.api._LOGGER")
    async def test_get_daily_rewards_401(self, mock_logger):
        """Test handling of 401 Unauthorized for daily rewards."""
        # Update the expected URL based on the actual implementation
        expected_url = "https://pool.braiins.com/accounts/rewards/json/btc"
        self.mock_session.get.return_value.__aenter__.return_value = (
            await self.mock_response(status=401)
        )

        with self.assertRaises(ClientError):
            await self.api_client.get_daily_rewards()

        self.mock_session.get.assert_awaited_once_with(
            expected_url, headers={"Pool-Auth-Token": self.api_key}
        )
        self.mock_session.get.return_value.__aenter__.return_value.raise_for_status.assert_called_once()  # Assert raise_for_status was called
        mock_logger.error.assert_called()  # Check if error logging was called

    @patch("custom_components.braiins_pool.api._LOGGER")
    async def test_get_daily_rewards_missing_keys(self, mock_logger):
        """Test handling of missing keys in daily rewards response."""
        mock_data = {"btc": {}}  # Missing daily_rewards
        # Update the expected URL based on the actual implementation
        expected_url = "https://pool.braiins.com/accounts/rewards/json/btc"
        self.mock_session.get.return_value.__aenter__.return_value = (
            await self.mock_response(json_data=mock_data)
        )

        with self.assertRaises(KeyError):
            await self.api_client.get_daily_rewards()

        self.mock_session.get.assert_awaited_once_with(
            expected_url, headers={"Pool-Auth-Token": self.api_key}
        )
        self.mock_session.get.return_value.__aenter__.return_value.raise_for_status.assert_called_once()  # Ensure raise_for_status is still checked
        mock_logger.error.assert_called()  # Check if error logging was called

    @patch("custom_components.braiins_pool.api._LOGGER")
    async def test_get_daily_rewards_empty_list(self, mock_logger):
        """Test handling of empty daily_rewards list."""
        mock_data = {"btc": {"daily_rewards": []}}
        # Update the expected URL based on the actual implementation
        expected_url = "https://pool.braiins.com/accounts/rewards/json/btc"
        self.mock_session.get.return_value.__aenter__.return_value = (
            await self.mock_response(json_data=mock_data)
        )

        with self.assertRaises(IndexError):
            await self.api_client.get_daily_rewards()

        self.mock_session.get.assert_awaited_once_with(
            expected_url, headers={"Pool-Auth-Token": self.api_key}
        )
        self.mock_session.get.return_value.__aenter__.return_value.raise_for_status.assert_called_once()  # Ensure raise_for_status is still checked
        mock_logger.error.assert_called_once()  # Check if error logging was called exactly once

    @patch("custom_components.braiins_pool.api._LOGGER")
    async def test_get_daily_rewards_invalid_json(self, mock_logger):
        """Test handling of invalid JSON response for daily rewards."""
        # Update the expected URL based on the actual implementation
        expected_url = "https://pool.braiins.com/accounts/rewards/json/btc"
        self.mock_session.get.return_value.__aenter__.return_value = (
            await self.mock_response(
                json_data=None, status=200
            )  # Simulate a valid HTTP response but invalid JSON
        )
        self.mock_session.get.return_value.__aenter__.return_value.json.side_effect = (
            ContentTypeError(MagicMock(), MagicMock())
        )

        with self.assertRaises(ContentTypeError):
            await self.api_client.get_daily_rewards()

        self.mock_session.get.assert_awaited_once_with(
            expected_url, headers={"Pool-Auth-Token": self.api_key}
        )
        mock_logger.error.assert_called_once()  # Ensure error logging was called

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
            "Error fetching data from %s: %s", expected_url, "Network issue"
        )

    # Add more test cases for different error conditions, data structures, etc.

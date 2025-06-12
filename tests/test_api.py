import logging
import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, patch, MagicMock

logging.basicConfig(level=logging.DEBUG)

import pytest

import aiohttp
from aiohttp import ClientError

from custom_components.braiins_pool.api import BraiinsPoolApiClient, BraiinsPoolApiException # Added BraiinsPoolApiException

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def api_client_fixture():
    mock_session = AsyncMock()
    mock_session.get = MagicMock()
    api_key = "test_api_key"
    client = BraiinsPoolApiClient(mock_session, api_key)
    return client, mock_session, api_key

class JustAMockResponse:
    def __init__(self, status=200, json_data=None, text_data="", message=""):
        self.status = status
        self._json_data = json_data if json_data is not None else {}
        self._text_data = text_data
        self.message = message
        self.raise_for_status = MagicMock()
        if status >= 400:
            mock_request_info = MagicMock()
            mock_request_info.url = "mock://url"
            mock_request_info.method = "GET"
            mock_request_info.headers = {}

            self.raise_for_status.side_effect = aiohttp.ClientResponseError(
                request_info=mock_request_info,
                history=tuple(),
                status=status,
                message=message or f"Mock HTTP error {status}",
                headers=None,
            )

    async def json(self):
        return self._json_data

    async def text(self):
        return self._text_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

def mock_response_factory(status=200, json_data=None, text_data="", message=""):
    return JustAMockResponse(status=status, json_data=json_data, text_data=text_data, message=message)

@patch("custom_components.braiins_pool.api.BraiinsPoolApiClient._LOGGER")
async def test_get_account_stats_success(mock_logger, api_client_fixture):
    api_client, mock_session, api_key = api_client_fixture
    mock_data = {"test": "data"}
    mock_session.get.return_value = mock_response_factory(json_data=mock_data)

    data = await api_client.get_account_stats()

    mock_session.get.assert_called_once_with(
        "https://pool.braiins.com/stats/json/btc",
        headers={"Pool-Auth-Token": api_key},
    )
    assert data == mock_data
    mock_logger.debug.assert_called()

@patch("custom_components.braiins_pool.api.BraiinsPoolApiClient._LOGGER")
async def test_get_account_stats_401(mock_logger, api_client_fixture):
    api_client, mock_session, api_key = api_client_fixture
    mock_response_obj = mock_response_factory(status=401, text_data="Unauthorized", message="Unauthorized")
    mock_session.get.return_value = mock_response_obj

    with pytest.raises(BraiinsPoolApiException): # Changed from ClientError
        await api_client.get_account_stats()

    mock_session.get.assert_called_once_with(
        "https://pool.braiins.com/stats/json/btc",
        headers={"Pool-Auth-Token": api_key},
    )
    mock_response_obj.raise_for_status.assert_called_once()
    mock_logger.error.assert_called()


@patch("custom_components.braiins_pool.api.BraiinsPoolApiClient._LOGGER")
async def test_get_account_stats_other_error(mock_logger, api_client_fixture):
    api_client, mock_session, api_key = api_client_fixture
    mock_response_obj = mock_response_factory(status=500, text_data="Server Error", message="Server Error")
    mock_session.get.return_value = mock_response_obj

    with pytest.raises(BraiinsPoolApiException): # Changed from ClientError
        await api_client.get_account_stats()

    mock_session.get.assert_called_once_with(
        "https://pool.braiins.com/stats/json/btc",
        headers={"Pool-Auth-Token": api_key},
    )
    mock_response_obj.raise_for_status.assert_called_once()
    mock_logger.error.assert_called()


@patch("custom_components.braiins_pool.api.BraiinsPoolApiClient._LOGGER")
async def test_get_daily_rewards_success(mock_logger, api_client_fixture):
    api_client, mock_session, api_key = api_client_fixture
    mock_data = {"btc": {"daily_rewards": [{"total_reward": "0.12345"}]}}
    mock_session.get.return_value = mock_response_factory(json_data=mock_data)
    data = await api_client.get_daily_rewards()
    mock_session.get.assert_called_once_with(
        "https://pool.braiins.com/accounts/rewards/json/btc",
        headers={"Pool-Auth-Token": api_key},
    )
    assert data == mock_data
    mock_logger.debug.assert_called()

@patch("custom_components.braiins_pool.api.BraiinsPoolApiClient._LOGGER")
async def test_get_daily_rewards_401(mock_logger, api_client_fixture):
    api_client, mock_session, api_key = api_client_fixture
    mock_response_obj = mock_response_factory(status=401, text_data="Unauthorized", message="Unauthorized")
    mock_session.get.return_value = mock_response_obj

    with pytest.raises(BraiinsPoolApiException): # Changed from ClientError
        await api_client.get_daily_rewards()

    mock_session.get.assert_called_once_with(
        "https://pool.braiins.com/accounts/rewards/json/btc",
        headers={"Pool-Auth-Token": api_key},
    )
    mock_response_obj.raise_for_status.assert_called_once()
    mock_logger.error.assert_called()


@patch("custom_components.braiins_pool.api.BraiinsPoolApiClient._LOGGER")
async def test_get_daily_rewards_client_error(mock_logger, api_client_fixture):
    api_client, mock_session, api_key = api_client_fixture
    expected_url = "https://pool.braiins.com/accounts/rewards/json/btc"
    mock_session.get.side_effect = ClientError("Network issue")

    with pytest.raises(ClientError) as excinfo: # This should still be ClientError as it's a direct network error
        await api_client.get_daily_rewards()

    assert "Network issue" in str(excinfo.value)
    mock_session.get.assert_called_once_with(
        expected_url, headers={"Pool-Auth-Token": api_key}
    )
    mock_logger.debug.assert_called()
    mock_logger.error.assert_not_called()


@patch("custom_components.braiins_pool.api.BraiinsPoolApiClient._LOGGER")
async def test_get_user_profile_success(mock_logger, api_client_fixture):
    api_client, mock_session, api_key = api_client_fixture
    mock_data = {"test": "user_profile_data"}
    mock_session.get.return_value = mock_response_factory(json_data=mock_data)
    data = await api_client.get_user_profile()
    mock_session.get.assert_called_once_with(
        "https://pool.braiins.com/accounts/profile/json/btc/",
        headers={"Pool-Auth-Token": api_key},
    )
    assert data == mock_data
    mock_logger.debug.assert_called()

@patch("custom_components.braiins_pool.api.BraiinsPoolApiClient._LOGGER")
async def test_get_daily_hashrate_success(mock_logger, api_client_fixture):
    api_client, mock_session, api_key = api_client_fixture
    mock_data = {"test": "daily_hashrate_data"}
    mock_session.get.return_value = mock_response_factory(json_data=mock_data)
    data = await api_client.get_daily_hashrate()
    mock_session.get.assert_called_once_with(
        "https://pool.braiins.com/accounts/hash_rate_daily/json/user/btc",
        headers={"Pool-Auth-Token": api_key},
    )
    assert data == mock_data
    mock_logger.debug.assert_called()

@patch("custom_components.braiins_pool.api.BraiinsPoolApiClient._LOGGER")
async def test_get_block_rewards_success(mock_logger, api_client_fixture):
    api_client, mock_session, api_key = api_client_fixture
    mock_data = {"test": "block_rewards_data"}
    from_date = "2023-10-01"
    to_date = "2023-10-07"
    mock_session.get.return_value = mock_response_factory(json_data=mock_data)
    data = await api_client.get_block_rewards(from_date, to_date)
    mock_session.get.assert_called_once_with(
        f"https://pool.braiins.com/accounts/block_rewards/json/btc?from={from_date}&to={to_date}",
        headers={"Pool-Auth-Token": api_key},
    )
    assert data == mock_data
    mock_logger.debug.assert_called()

@patch("custom_components.braiins_pool.api.BraiinsPoolApiClient._LOGGER")
async def test_get_workers_success(mock_logger, api_client_fixture):
    api_client, mock_session, api_key = api_client_fixture
    mock_data = {"test": "workers_data"}
    mock_session.get.return_value = mock_response_factory(json_data=mock_data)
    data = await api_client.get_workers()
    mock_session.get.assert_called_once_with(
        "https://pool.braiins.com/accounts/workers/json/btc/",
        headers={"Pool-Auth-Token": api_key},
    )
    assert data == mock_data
    mock_logger.debug.assert_called()

@patch("custom_components.braiins_pool.api.BraiinsPoolApiClient._LOGGER")
async def test_get_payouts_success(mock_logger, api_client_fixture):
    api_client, mock_session, api_key = api_client_fixture
    mock_data = {"test": "payouts_data"}
    from_date = "2023-10-01"
    to_date = "2023-10-07"
    mock_session.get.return_value = mock_response_factory(json_data=mock_data)
    data = await api_client.get_payouts(from_date, to_date)
    mock_session.get.assert_called_once_with(
        f"https://pool.braiins.com/accounts/payouts/json/btc?from={from_date}&to={to_date}",
        headers={"Pool-Auth-Token": api_key},
    )
    assert data == mock_data
    mock_logger.debug.assert_called()

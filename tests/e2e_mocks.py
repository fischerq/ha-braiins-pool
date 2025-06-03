# tests/e2e_mocks.py

import json
from unittest.mock import AsyncMock, MagicMock

# --- Mocking Successful API Responses ---

def mock_successful_stats_response(mocker):
    """Mocks a successful response from the Braiins Pool stats endpoint."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers = {'Content-Type': 'application/json'}

    # Sample successful stats data - adjust based on the actual API response
    success_data = {
        "current_balance": "0.00123456",
        "all_time_reward": "1.50000000",
        # Add other relevant stats data from the API response
    }

    mock_response.json = AsyncMock(return_value=success_data)
    mock_response.release = AsyncMock() # Mock release method

    # Mock the get method of aiohttp.ClientSession
    mock_get = AsyncMock(return_value=mock_response)
    mocker.patch('aiohttp.ClientSession.get', new=mock_get)

def mock_successful_daily_rewards_response(mocker):
    """Mocks a successful response from the Braiins Pool daily rewards endpoint."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers = {'Content-Type': 'application/json'}

    # Sample successful daily rewards data - adjust based on the actual API response structure
    success_data = {
        "btc": {
            "daily_rewards": [
                {
                    "date": 1627862400,
                    "total_reward": "0.05000000",
                    "mining_reward": "0.04800000",
                    "bos_plus_reward": "0.00200000",
                    "referral_bonus": "0.00000000",
                    "referral_reward": "0.00000000",
                    "calculation_date": 1699840800
                }
            ]
        }
    }

    mock_response.json = AsyncMock(return_value=success_data)
    mock_response.release = AsyncMock()

    mock_get = AsyncMock(return_value=mock_response)
    mocker.patch('aiohttp.ClientSession.get', new=mock_get)

def mock_successful_all_responses(mocker):
    """Mocks successful responses from both stats and daily rewards endpoints."""
    stats_mock_response = MagicMock()
    stats_mock_response.status = 200
    stats_mock_response.headers = {'Content-Type': 'application/json'}
    stats_success_data = {
        "current_balance": "0.00123456",
        "all_time_reward": "1.50000000",
        # Add other relevant stats data
    }
    stats_mock_response.json = AsyncMock(return_value=stats_success_data)
    stats_mock_response.release = AsyncMock()

    daily_rewards_mock_response = MagicMock()
    daily_rewards_mock_response.status = 200
    daily_rewards_mock_response.headers = {'Content-Type': 'application/json'}
    daily_rewards_success_data = {
        "btc": {
            "daily_rewards": [
                {
                    "date": 1627862400,
                    "total_reward": "0.05000000",
                    "mining_reward": "0.04800000",
                    "bos_plus_reward": "0.00200000",
                    "referral_bonus": "0.00000000",
                    "referral_reward": "0.00000000",
                    "calculation_date": 1699840800
                }
            ]
        }
    }
    daily_rewards_mock_response.json = AsyncMock(return_value=daily_rewards_success_data)
    daily_rewards_mock_response.release = AsyncMock()

    # Mock the get method to return different responses based on the URL
    def side_effect_get(url, headers):
        if "stats/json/btc" in url:
            return stats_mock_response
        elif "accounts/rewards/json/btc" in url:
            return daily_rewards_mock_response
        return MagicMock(status=404) # Default for unknown URLs

    mock_get = AsyncMock(side_effect=side_effect_get)
    mocker.patch('aiohttp.ClientSession.get', new=mock_get)


# --- Mocking Error API Responses ---

def mock_api_error_response(mocker, status_code: int, error_message: str = "API Error"):
    """Mocks an API response with a specific HTTP status code and error message."""
    mock_response = MagicMock()
    mock_response.status = status_code
    mock_response.headers = {'Content-Type': 'application/json'}
    mock_response.reason = error_message # Simulate reason phrase
    mock_response.text = AsyncMock(return_value=json.dumps({"error": error_message})) # Simulate error body
    mock_response.release = AsyncMock()

    mock_get = AsyncMock(return_value=mock_response)
    mocker.patch('aiohttp.ClientSession.get', new=mock_get)

def mock_connection_error(mocker):
    """Mocks a connection error during the API call."""
    mock_get = AsyncMock(side_effect=aiohttp.ClientConnectorError(None, None)) # Simulate connection error
    mocker.patch('aiohttp.ClientSession.get', new=mock_get)

def mock_json_decode_error(mocker):
    """Mocks a response that is not valid JSON."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers = {'Content-Type': 'application/json'}
    mock_response.json = AsyncMock(side_effect=json.JSONDecodeError("Invalid JSON", "{}", 0)) # Simulate JSON decode error
    mock_response.release = AsyncMock()

    mock_get = AsyncMock(return_value=mock_response)
    mocker.patch('aiohttp.ClientSession.get', new=mock_get)

# Example usage within a test function (requires a testing framework like pytest with mocker)
# def test_successful_data_fetch(mocker):
#     mock_successful_all_responses(mocker)
#     # Now run your Home Assistant integration setup and verify sensors
#     pass

# def test_api_unauthorized(mocker):
#     mock_api_error_response(mocker, 401, "Invalid API Key")
#     # Now run your Home Assistant integration setup and verify error handling
#     pass
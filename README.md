## Braiins Pool Home Assistant Integration

Monitor your Braiins Pool mining statistics, account data, and worker performance directly within Home Assistant. This integration fetches a variety of data points from the Braiins Pool API to provide insights into your mining operations.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=braiins_pool)

### Installation

This integration is available through HACS (Home Assistant Community Store).

1.  **Add this repository as a Custom Repository in HACS.**
    *   In HACS, go to the Integrations tab.
    *   Click on the three dots in the top right corner and select `Custom repositories`.
    *   Enter the URL of this repository (`https://github.com/fischerq/ha-braiins-pool/`) and select the category `Integration`.
    *   Click `Add`.
1.  **Install the integration.**
    *   Search for "Braiins Pool" in the HACS Integrations tab.
    *   Click "Download" and restart Home Assistant.
1.  **Add the Braiins Pool integration.**
    *   Go to Settings -> Devices & Services -> Add Integration.
    *   Search for Braiins Pool` and select it.
    *   Enter your Braiins Pool API Key when prompted.
    *   To obtain your API key, follow the instructions in the Braiins Pool API     
        documentation: [https://academy.braiins.com/en/braiins-pool/monitoring/#api-configuration](https://academy.braiins.com/en/braiins-pool/monitoring/#api-configuration)

### Sensors

This integration will create sensors for:

*   `today_reward`: Braiins Pool Today's Reward
*   `current_balance`: Braiins Pool Current Balance
*   `all_time_reward`: Braiins Pool All Time Reward
*   `pool_5m_hash_rate`: Braiins Pool 5m Hash Rate
*   `ok_workers`: Braiins Pool Active Workers
*   `today_reward_satoshi`: Braiins Pool Today's Reward Satoshi
*   `current_balance_satoshi`: Braiins Pool Current Balance Satoshi
*   `all_time_reward_satoshi`: Braiins Pool All Time Reward Satoshi

### Disclaimer

Please be mindful of the Braiins Pool API rate limits. The integration is designed to poll the API periodically, but excessive polling or other API usage might lead to temporary blocks. The default update interval is set to respect the documented rate limits.

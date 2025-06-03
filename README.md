## Braiins Pool Home Assistant Integration

Monitor your Braiins Pool mining rewards and account statistics directly within Home Assistant. This integration allows you to track your daily rewards, current balance, and potentially other metrics exposed by the Braiins Pool API.

### Installation

This integration is available through HACS (Home Assistant Community Store).

1.  **Add this repository as a Custom Repository in HACS.**
    *   In HACS, go to the Integrations tab.
    *   Click on the three dots in the top right corner and select "Custom repositories".
    *   Enter the URL of this repository (`https://github.com/your_github_username/homeassistant-braiins-pool` - replace with the actual URL) and select the category "Integration".
    *   Click "Add".
2.  **Install the integration.**
    *   Search for "Braiins Pool" in the HACS Integrations tab.
    *   Click "Download" and restart Home Assistant.

### Configuration

1.  **Add the Braiins Pool integration.**
    *   Go to Settings -> Devices & Services -> Add Integration.
    *   Search for "Braiins Pool" and select it.
    *   Enter your Braiins Pool API Key when prompted.
    *   [Add instructions on how to obtain the API key from Braiins Pool here]

### Sensors

This integration will create sensors for:

*   Daily Mining Reward
*   Current Account Balance
*   All-Time Reward
*   [List any other sensors you implement]

### Disclaimer

Please be mindful of the Braiins Pool API rate limits. The integration is designed to poll the API periodically, but excessive polling or other API usage might lead to temporary blocks. The default update interval is set to respect the documented rate limits.
## Braiins Pool Home Assistant Integration

Monitor your Braiins Pool mining rewards and account statistics directly within Home Assistant. This integration allows you to track your daily rewards, current balance, and potentially other metrics exposed by the Braiins Pool API.

### Installation

This integration is available through HACS (Home Assistant Community Store).

1.  **Add this repository as a Custom Repository in HACS.**
    *   In HACS, go to the Integrations tab.
    *   Click on the three dots in the top right corner and select "Custom repositories".
    *   Enter the URL of this repository (`https://github.com/your_github_username/homeassistant-braiins-pool` - replace with the actual URL) and select the category "Integration".
    *   Click "Add".
2.  **Install the integration.**
    *   Search for "Braiins Pool" in the HACS Integrations tab.
    *   Click "Download" and restart Home Assistant.

### Configuration

1.  **Add the Braiins Pool integration.**
    *   Go to Settings -> Devices & Services -> Add Integration.
    *   Search for "Braiins Pool" and select it.
    *   Enter your Braiins Pool API Key when prompted.
    *   [Add instructions on how to obtain the API key from Braiins Pool here]

### Sensors

This integration will create sensors for:

*   Daily Mining Reward
*   Current Account Balance
*   All-Time Reward
*   [List any other sensors you implement]

### Disclaimer

Please be mindful of the Braiins Pool API rate limits. The integration is designed to poll the API periodically, but excessive polling or other API usage might lead to temporary blocks. The default update interval is set to respect the documented rate limits.

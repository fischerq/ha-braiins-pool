#!/bin/bash

# This script is for running Home Assistant in a development environment
# with the braiins_pool custom component loaded.
# You will need to adapt the paths and commands below to your specific setup.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Path to your Home Assistant virtual environment activate script
# Example: HASS_VENV_ACTIVATE="/path/to/your/hass_dev_venv/bin/activate"
HASS_VENV_ACTIVATE=""

# Path to your Home Assistant configuration directory for development
# This directory should contain your configuration.yaml and the custom_components folder
# Example: HASS_CONFIG_DIR="/path/to/your/hass_config"
HASS_CONFIG_DIR=""

# --- Script ---

# Check if configuration variables are set
if [ -z "$HASS_VENV_ACTIVATE" ] || [ -z "$HASS_CONFIG_DIR" ]; then
  echo "ERROR: Please update the HASS_VENV_ACTIVATE and HASS_CONFIG_DIR variables in this script."
  exit 1
fi

echo "Activating Home Assistant virtual environment..."
# Activate the virtual environment
source "$HASS_VENV_ACTIVATE"

echo "Running Home Assistant with configuration directory: $HASS_CONFIG_DIR"
# Run Home Assistant
# The '-c' flag specifies the configuration directory
hass -c "$HASS_CONFIG_DIR"

echo "Home Assistant stopped."
#!/bin/bash

# This script is used to run the unit tests for the Braiins Pool Home Assistant integration.

# Remember to activate your Python virtual environment if you are using one:
# source venv/bin/activate

# Option 1: Run tests using Python's built-in unittest module
python -m unittest discover tests

# Option 2: Run tests using pytest (uncomment the line below if you have pytest installed and prefer it)
# pytest tests
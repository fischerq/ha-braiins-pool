#!/bin/bash

# This script is used to run the unit tests for the Braiins Pool Home Assistant integration.

PYTHONPATH=.
echo "running ls"
ls .
echo "echo pypath"
echo $PYTHONPATH
pytest tests/
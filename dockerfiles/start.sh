#!/bin/bash
printenv

# Run the Python script to replace the placeholders in the configuration file
python3.10 /replace_placeholders.py

# Start the application
exec python3.10 /spellbook/spellbookserver.py
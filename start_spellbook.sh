#!/bin/sh
sleep 10
source /spellbook/venv/bin/activate
nix-shell -p openssl
python /spellbook/spellbookserver.py
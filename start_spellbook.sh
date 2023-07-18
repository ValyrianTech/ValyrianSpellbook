#!/bin/sh
sleep 10
source /spellbook/venv/bin/activate
OPENSSL_BIN=${pkgs.openssl}/bin/openssl
export PATH="$OPENSSL_BIN:$PATH"
python /spellbook/spellbookserver.py
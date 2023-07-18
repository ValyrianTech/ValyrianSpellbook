#!/bin/sh
sleep 10
source /spellbook/venv/bin/activate
export OPENSSL_CONF=${pkgs.openssl.dev}/etc/ssl/openssl.cnf
python /spellbook/spellbookserver.py
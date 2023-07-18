source /spellbook/venv/bin/activate
nix-shell -p openssl --run "python /spellbook/spellbookserver.py > /tmp/spellbookserver.log 2>&1 || echo $? > /tmp/spellbookserver_exit_status"

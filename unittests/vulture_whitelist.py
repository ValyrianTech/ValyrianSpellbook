# Vulture whitelist. Every identifier referenced below is treated as "used"
# by vulture. Pytest fixtures (autouse=True) are invoked via framework magic
# rather than direct calls, so static analysis cannot see them being used.

# Pytest autouse fixtures.
_mock_valid_webhook_url
